# run_batch.py
import os
import csv
import time
import shutil
import tempfile
import logging
import multiprocessing
import numpy as np
import pandas as pd
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import platform

# Import các module cốt lõi
from hierarchy_loader import HierarchyLoader
from aro_apo_optimizer import aro_apo_optimization
from utils import genetic_algorithm_optimization, pso_optimization
from classifier import calculate_accuracy
import config  # Import config gốc
from run_parallel import analyze_and_suggest_params, run_single_trial # Tận dụng hàm từ file cũ

# =============================================================================
# CẤU HÌNH DANH SÁCH DATASET (BẠN SỬA Ở ĐÂY)
# =============================================================================
# Chỉ để lại 2 bộ chưa chạy
DATASETS = ["italia", "cmc", "mgm", "cahousing", "adult", "medical"]

# Cấu hình chạy
NUM_TRIALS = 1      # Số lần chạy mỗi thuật toán/mỗi dataset
MAX_WORKERS = 10     # Số luồng song song

# =============================================================================
# LOGIC CHẠY BATCH
# =============================================================================
def run_dataset_experiment(dataset_name):
    print(f"\n" + "#"*80)
    print(f"📦 ĐANG XỬ LÝ DATASET: {dataset_name.upper()}")
    print("#"*80)

    # 1. CẬP NHẬT CONFIG ĐỘNG (Dynamic Monkey-Patching)
    # Vì config.py là tĩnh, ta phải sửa đường dẫn runtime
    config.DATASET_NAME = dataset_name
    config.DATA_DIR = config.BASE_DIR / "data" / dataset_name
    config.INPUT_FILE = config.DATA_DIR / f"{dataset_name}.csv"
    config.HIERARCHY_DIR = config.DATA_DIR / "hierarchies"
    config.TRAIN_TEST_DIR = config.DATA_DIR # Để tính accuracy gốc
    
    # Kiểm tra file tồn tại
    if not config.INPUT_FILE.exists():
        print(f"⚠️ Bỏ qua {dataset_name}: Không tìm thấy file {config.INPUT_FILE}")
        return None

    # 2. Gợi ý tham số (k, l, c) riêng cho dataset này
    # Lưu ý: SENSITIVE_ATTRIBUTE có thể khác nhau mỗi dataset. 
    # Ở đây giả sử bạn đã set đúng hoặc dùng cột cuối cùng.
    # Nếu mỗi dataset có cột nhạy cảm khác nhau, bạn cần 1 dictionary map tên dataset -> tên cột.
    sensitive_map = {
        "medical": "PrimaryDiagnosis"
        # Thêm các dataset khác vào đây nếu cần, nếu không code sẽ tự lấy cột cuối
    }
    sen_attr = sensitive_map.get(dataset_name, config.SENSITIVE_ATTRIBUTE)
    
    s_k, s_l, s_c = analyze_and_suggest_params(config.INPUT_FILE, sen_attr)
    print(f"📌 Tham số tự động cho {dataset_name}: k={s_k}, l={s_l}, c={s_c}")

    # 3. Tính Baseline Accuracy
    try:
        baseline_acc = calculate_accuracy(config.INPUT_FILE, save_split=True)
        print(f"✅ Baseline Accuracy: {baseline_acc:.6f}")
    except Exception as e:
        print(f"⚠️ Lỗi Baseline: {e}")
        baseline_acc = 0.0

    # 4. Chuẩn bị tác vụ chạy song song
    RUN_PARAMS = config.ARO_PARAMS.copy()
    RUN_PARAMS['log_every'] = 99999
    RUN_PARAMS['patience'] = 10
    
    algorithms = [
        ("ARO-APO", aro_apo_optimization)
        # ,("GA", genetic_algorithm_optimization),
        # ("PSO", pso_optimization)
    ]

    results = []
    
    '''
    Chúng ta phải truyền config paths vào hàm worker vì biến toàn cục config
    có thể không đồng bộ giữa các process con nếu không cẩn thận.
    Tuy nhiên, hàm run_single_trial hiện tại dựa vào biến global config đã import.
    Để an toàn nhất, trong run_single_trial ta cần reload lại HierarchyLoader
    với đường dẫn mới. (Đã xử lý trong run_parallel.py cũ: nó gọi HierarchyLoader(HIERARCHY_DIR))
    Nhưng HIERARCHY_DIR ở file run_parallel cũ là import tĩnh.
    -> CẦN TRUYỀN HIERARCHY_DIR VÀ INPUT_FILE VÀO run_single_trial.
    
    SỬA NHANH: Định nghĩa lại run_single_trial wrapper ở đây để chốt cứng đường dẫn
    trước khi gửi sang process con
    '''
    current_input_file = str(config.INPUT_FILE)
    current_hierarchy_dir = str(config.HIERARCHY_DIR)

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for algo_name, algo_func in algorithms:
            for i in range(1, NUM_TRIALS + 1):
                # Truyền params explicit để tránh lỗi global variable
                task_params = RUN_PARAMS.copy()
                # Hack: ta truyền input_file và hierarchy_dir qua params để hàm worker biết
                task_params['_override_input'] = current_input_file
                task_params['_override_hierarchy'] = current_hierarchy_dir
                
                futures.append(
                    executor.submit(
                        run_worker_wrapper, # Hàm wrapper mới (xem dưới)
                        algo_name, algo_func, i, 
                        s_k, s_l, s_c, task_params, baseline_acc, 
                        current_input_file, current_hierarchy_dir
                    )
                )
        
        completed = 0
        total = len(algorithms) * NUM_TRIALS
        for future in as_completed(futures):
            res = future.result()
            completed += 1
            if res:
                res['Dataset'] = dataset_name # Gán nhãn Dataset
                results.append(res)
                print(f"[{dataset_name} {completed}/{total}] ✅ {res['Algorithm']} (Run {res['Run_ID']}) | Fit: {res['Best_Fitness']:.2f}")

    return pd.DataFrame(results)

# Hàm Wrapper để xử lý process con chạy đúng đường dẫn dataset hiện tại
def run_worker_wrapper(algo_name, algo_func, run_id, k, l, c, params, baseline_acc, input_file_path, hierarchy_dir_path):
    # 1. Setup lại config global trong process con cho khớp dataset hiện tại
    config.INPUT_FILE = Path(input_file_path)
    config.HIERARCHY_DIR = Path(hierarchy_dir_path)
    # Cần set biến global module INPUT_FILE trong run_parallel gốc nếu nó dùng
    # Nhưng tốt nhất ta dùng hàm run_single_trial đã sửa, và truyền đè tham số
    
    # 2. Gọi hàm run_single_trial gốc (nhưng ta cần sửa run_single_trial để nhận path đè)
    # Thay vì sửa file gốc, ta copy logic run_single_trial vào đây cho an toàn (Self-contained)
    
    temp_root = None
    if platform.system() == 'Linux' and os.path.exists('/dev/shm'): temp_root = '/dev/shm'
    temp_dir = tempfile.mkdtemp(prefix=f"run_{algo_name}_{run_id}_", dir=temp_root)
    
    # Override Config
    config.TRAIN_TEST_DIR = Path(temp_dir)
    params['temp_dir'] = str(temp_dir)
    
    # Xóa key nội bộ
    if '_override_input' in params: del params['_override_input']
    if '_override_hierarchy' in params: del params['_override_hierarchy']

    local_loader = HierarchyLoader(hierarchy_dir_path) # Load đúng thư mục
    
    try:
        output_file = Path(temp_dir) / f"res_{run_id}.csv"
        start_time = time.time()
        
        best_x, best_f, history, info_loss, k_viol, l_viol = algo_func(
            hierarchy_loader=local_loader,
            input_file=input_file_path, # Load đúng file
            k=k, l=l, c=c,
            output_file=output_file,
            **params
        )
        
        execution_time = time.time() - start_time
        acc_after = 0.0
        if output_file.exists():
            try: acc_after = calculate_accuracy(output_file)
            except: acc_after = 0.0
        
        hist_list = list(history) if not isinstance(history, list) else history
        min_val = min(hist_list) if hist_list else 0
        iterations = hist_list.index(min_val) + 1 if hist_list else 0
        
        result = {
            "Dataset": "UNKNOWN", # Sẽ được update ở hàm cha
            "Algorithm": algo_name,
            "Run_ID": run_id,
            "Best_Fitness": best_f,
            "Info_Loss": info_loss,
            "Accuracy_Original": baseline_acc,
            "Accuracy_After": acc_after,
            "Execution_Time_s": execution_time,
            "K_Violations": k_viol,
            "L_Violations": l_viol,
            "Iterations": iterations,
            "Success": 1 if (k_viol == 0 and l_viol == 0) else 0,
            "Solution_Vector": str(list(best_x)),
            "Fitness_History": str(hist_list)
        }
        return result
    except Exception as e:
        print(f"ERROR Worker: {e}")
        return None
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    multiprocessing.freeze_support()
    print("🚀 BẮT ĐẦU CHẠY BATCH TRÊN TOÀN BỘ DATASETS")
    
    all_results = []
    
    for dataset in DATASETS:
        df_ds = run_dataset_experiment(dataset)
        if df_ds is not None and not df_ds.empty:
            all_results.append(df_ds)
            
            # Lưu tạm kết quả từng dataset đề phòng crash
            temp_save = config.RESULTS_DIR / f"TEMP_RES_{dataset}.csv"
            df_ds.to_csv(temp_save, index=False)
            print(f"💾 Đã lưu tạm kết quả {dataset}")

    if not all_results:
        print("❌ Không có kết quả nào.")
        return

# ... (Phần trên giữ nguyên) ...

    # =========================================================================
    # ĐOẠN CODE MỚI: GỘP TẤT CẢ (CŨ + MỚI)
    # =========================================================================
    
    # Danh sách ĐẦY ĐỦ 7 bộ dữ liệu bạn muốn có trong báo cáo cuối cùng
    # (Code sẽ đi tìm file TEMP_RES của các bộ này để ghép lại)
    FULL_DATASET_LIST = ["italia", "cmc", "mgm", "cahousing", "adult", "informs", "medical"]
    
    final_collection = []
    print("\n" + "-"*80)
    print("🔄 ĐANG TỔNG HỢP DỮ LIỆU TỪ Ổ CỨNG (CŨ + MỚI)...")
    
    for ds_name in FULL_DATASET_LIST:
        temp_file = config.RESULTS_DIR / f"TEMP_RES_{ds_name}.csv"
        
        if temp_file.exists():
            print(f"   📥 Đã nạp thành công: {ds_name} (từ {temp_file.name})")
            try:
                df_temp = pd.read_csv(temp_file)
                final_collection.append(df_temp)
            except Exception as e:
                print(f"   ❌ Lỗi khi đọc file {ds_name}: {e}")
        else:
            print(f"   ⚠️ CẢNH BÁO: Chưa tìm thấy kết quả của '{ds_name}'. Bảng tổng hợp sẽ thiếu bộ này.")

    if not final_collection:
        print("❌ Không tìm thấy bất kỳ dữ liệu nào để tổng hợp.")
        return

    # Gộp lại thành DataFrame lớn
    final_df = pd.concat(final_collection, ignore_index=True)
    
    # 1. Lưu Raw Data (Gồm đủ 7 bộ)
    raw_path = config.RESULTS_DIR / "MASTER_RAW_ALL_DATASETS.csv"
    final_df.to_csv(raw_path, index=False)
    
    # 2. Tính bảng tổng hợp (Mean ± Std)
    summary = final_df.groupby(['Dataset', 'Algorithm']).agg({
        'Best_Fitness': ['mean', 'std'],
        'Accuracy_After': ['mean', 'std'],
        'Execution_Time_s': ['mean', 'std'],
        'Iterations': ['mean'],
        'Success': ['mean']
    }).reset_index()
    
    # Làm đẹp tên cột
    summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in summary.columns.values]
    
    summary_path = config.RESULTS_DIR / "MASTER_SUMMARY_ALL_DATASETS.csv"
    summary.to_csv(summary_path, index=False)
    
    print("\n" + "="*80)
    print(f"🏆 HOÀN TẤT! Đã gom đủ {len(final_collection)}/{len(FULL_DATASET_LIST)} dataset.")
    print(f"📁 File tổng hợp: {summary_path}")
    print("="*80)

if __name__ == '__main__':
    main()