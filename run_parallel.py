# run_parallel.py
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
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
import math
import platform

# Import các module hiện có
from hierarchy_loader import HierarchyLoader
from aro_apo_optimizer import aro_apo_optimization
from utils import genetic_algorithm_optimization, pso_optimization
from classifier import calculate_accuracy
import config  # Import config để monkey-patch
from config import (
    INPUT_FILE, HIERARCHY_DIR, RESULTS_DIR, ARO_PARAMS,
    DATASET_NAME, K_ANONYMITY, L_DIVERSITY, C_RECURSIVE, SENSITIVE_ATTRIBUTE
)

# Tắt log để tránh spam màn hình khi chạy song song
logging.basicConfig(level=logging.ERROR)

# =============================================================================
# 1. CẤU HÌNH SỐ LƯỢNG CHẠY & LUỒNG
# =============================================================================
NUM_TRIALS = 30      # Số lần chạy mỗi thuật toán
MAX_WORKERS = 10     # Sử dụng 10 luồng xử lý

# =============================================================================
# 2. HÀM GỢI Ý THAM SỐ (GIỮ NGUYÊN)
# =============================================================================
def analyze_and_suggest_params(input_file, sensitive_attr):
    if not os.path.exists(input_file):
        return K_ANONYMITY, L_DIVERSITY, C_RECURSIVE

    sensitive_values = []
    total_rows = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames
        target_col = sensitive_attr if sensitive_attr in fieldnames else fieldnames[-1]
        
        for row in reader:
            total_rows += 1
            if target_col in row:
                sensitive_values.append(row[target_col])

    counts = Counter(sensitive_values)
    unique_count = len(counts)
    if unique_count == 0: return 2, 2, 1.0
    
    sorted_counts = sorted(counts.values(), reverse=True)
    r1 = sorted_counts[0]
    
    if total_rows < 500: suggested_k = 2
    elif total_rows < 10000: suggested_k = 5
    else: suggested_k = 10
    
    suggested_l = 2
    for i in range(1, min(unique_count, 5)):
        coverage_contribution = sorted_counts[i] / total_rows
        if coverage_contribution > 0.01: suggested_l = i + 1
        else: break
    
    suggested_l = min(suggested_l, 4)
    if unique_count < suggested_l: suggested_l = unique_count
    if suggested_l > suggested_k: suggested_l = suggested_k

    tail_sum = sum(sorted_counts[suggested_l-1:])
    c_global = float(r1) if tail_sum == 0 else r1 / tail_sum

    alpha = 2.5
    buffer = 1 + (alpha / math.sqrt(suggested_k))
    suggested_c = round(c_global * buffer, 2)
    if suggested_c < 1.1: suggested_c = 1.1

    return suggested_k, suggested_l, suggested_c

# =============================================================================
# 3. WORKER FUNCTION (CHẠY ĐƠN LẺ TRONG MỘT TIẾN TRÌNH)
# =============================================================================
# =============================================================================
# 3. WORKER FUNCTION (ĐÃ SỬA LỖI PERMISSION DENIED)
# =============================================================================
def run_single_trial(algo_name, algo_func, run_id, k, l, c, params, baseline_acc):
    """
    Hàm chạy trên Process riêng biệt.
    Sử dụng thư mục tạm để tránh xung đột file và tối ưu tốc độ I/O.
    """
    # Xử lý đường dẫn Temp tối ưu cho RAM
    temp_root = None
    if platform.system() == 'Linux' and os.path.exists('/dev/shm'):
        temp_root = '/dev/shm'
    
    # Tạo thư mục tạm riêng biệt
    temp_dir = tempfile.mkdtemp(prefix=f"run_{algo_name}_{run_id}_", dir=temp_root)
    
    # Monkey-patch (Phòng hờ)
    config.TRAIN_TEST_DIR = Path(temp_dir)
    
    # --- QUAN TRỌNG: THÊM DÒNG NÀY ---
    # Truyền đường dẫn temp này vào params để gửi xuống các thuật toán con
    params['temp_dir'] = str(temp_dir)
    # ---------------------------------

    # Load lại Hierarchy trong process con
    local_loader = HierarchyLoader(HIERARCHY_DIR)
    
    try:
        output_file = Path(temp_dir) / f"res_{run_id}.csv"
        start_time = time.time()
        
        # GỌI THUẬT TOÁN TỐI ƯU
        best_x, best_f, history, info_loss, k_viol, l_viol = algo_func(
            hierarchy_loader=local_loader,
            input_file=INPUT_FILE,
            k=k, l=l, c=c,
            output_file=output_file,
            **params  # <--- params giờ đã chứa 'temp_dir'
        )
        
        execution_time = time.time() - start_time
        
        # Tính Accuracy
        acc_after = 0.0
        if output_file.exists():
            try: acc_after = calculate_accuracy(output_file)
            except: acc_after = 0.0
        
        # Xác định vòng hội tụ
        hist_list = list(history) if not isinstance(history, list) else history
        min_val = min(hist_list)
        iterations = hist_list.index(min_val) + 1
        
        # Đóng gói kết quả
        result = {
            "Algorithm": algo_name,
            "Run_ID": run_id,
            "Best_Fitness": best_f,
            "Info_Loss": info_loss,
            "Accuracy_Original": baseline_acc,
            "Accuracy_After": acc_after,
            "Accuracy_Loss": baseline_acc - acc_after,
            "Execution_Time_s": execution_time,
            "K_Violations": k_viol,
            "L_Violations": l_viol,
            "Iterations": iterations,
            "Success": 1 if (k_viol == 0 and l_viol == 0) else 0,
            "Solution_Vector": str(list(best_x)) 
        }
        
        return result

    except Exception as e:
        print(f"❌ Lỗi tại {algo_name} Run {run_id}: {e}")
        # In traceback để dễ debug nếu cần
        # import traceback; traceback.print_exc()
        return None
    finally:
        # Xóa ngay thư mục tạm để giải phóng RAM/Disk
        shutil.rmtree(temp_dir, ignore_errors=True)

# =============================================================================
# 4. TRÌNH QUẢN LÝ SONG SONG (MAIN)
# =============================================================================
def main():
    print("\n" + "="*80)
    print("🚀 HỆ THỐNG CHẠY THỰC NGHIỆM SONG SONG (PARALLEL BENCHMARK)")
    print(f"⚡ Cấu hình: {MAX_WORKERS} luồng | {NUM_TRIALS} lần chạy/thuật toán")
    print("="*80)

    # 1. Gợi ý tham số
    s_k, s_l, s_c = analyze_and_suggest_params(INPUT_FILE, SENSITIVE_ATTRIBUTE)
    print(f"📌 Tham số áp dụng: k={s_k}, l={s_l}, c={s_c}")

    # 2. Tính Baseline Accuracy
    print("⏳ Đang tính Baseline Accuracy...")
    try:
        baseline_acc = calculate_accuracy(INPUT_FILE, save_split=True)
        print(f"✅ Baseline Accuracy: {baseline_acc:.6f}")
    except Exception as e:
        print(f"⚠️ Lỗi tính Baseline: {e}")
        baseline_acc = 0.0

    # 3. Chuẩn bị tác vụ
    tasks = []
    RUN_PARAMS = ARO_PARAMS.copy()
    RUN_PARAMS['log_every'] = 99999 # Tắt log con
    RUN_PARAMS['patience'] = 10     # Giữ patience an toàn

    algorithms = [
        ("ARO-APO", aro_apo_optimization),
        ("GA", genetic_algorithm_optimization),
        ("PSO", pso_optimization)
    ]

    total_tasks = len(algorithms) * NUM_TRIALS
    print(f"\n📦 Tổng cộng {total_tasks} tác vụ. Bắt đầu chạy...")

    results = []
    start_global = time.time()

    # 4. Chạy song song
    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for algo_name, algo_func in algorithms:
            for i in range(1, NUM_TRIALS + 1):
                futures.append(
                    executor.submit(
                        run_single_trial, 
                        algo_name, algo_func, i, 
                        s_k, s_l, s_c, RUN_PARAMS, baseline_acc
                    )
                )
        
        completed = 0
        for future in as_completed(futures):
            res = future.result()
            completed += 1
            if res:
                results.append(res)
                print(f"[{completed}/{total_tasks}] ✅ {res['Algorithm']} (Run {res['Run_ID']}) | Fit: {res['Best_Fitness']:.4f} | It: {res['Iterations']} | Time: {res['Execution_Time_s']:.1f}s")
            else:
                print(f"[{completed}/{total_tasks}] ❌ Lỗi tác vụ.")

    total_time = time.time() - start_global
    print(f"\n🏁 Hoàn tất trong {total_time/60:.2f} phút.")

    # =========================================================================
    # 5. TỔNG HỢP & LƯU KẾT QUẢ
    # =========================================================================
    if not results: return

    df = pd.DataFrame(results)
    df = df.sort_values(by=['Algorithm', 'Run_ID'])

    # FILE 1: RAW DATA (Dùng cho Boxplot & Phân tích chi tiết)
    # Có chứa cột Solution_Vector như yêu cầu
    raw_file = RESULTS_DIR / f"{DATASET_NAME}_parallel_raw_k{s_k}_l{s_l}_c{s_c}.csv"
    df.to_csv(raw_file, index=False)
    print(f"\n💾 Dữ liệu thô (kèm Vector nghiệm): {raw_file}")

    # FILE 2: SUMMARY STATISTICS (Mean ± Std)
    # Tìm vector tốt nhất (Best Ever) cho mỗi thuật toán để hiển thị
    best_configs = df.loc[df.groupby("Algorithm")["Best_Fitness"].idxmin()][["Algorithm", "Solution_Vector", "Best_Fitness"]]
    best_configs.rename(columns={"Solution_Vector": "Best_Solution_Vector_Found", "Best_Fitness": "Min_Fitness_Ever"}, inplace=True)

    summary = df.groupby('Algorithm').agg({
        'Best_Fitness': ['mean', 'std'],
        'Info_Loss': ['mean', 'std'],
        'Accuracy_After': ['mean', 'std'],
        'Execution_Time_s': ['mean', 'std'],
        'Iterations': ['mean', 'std'],
        'Success': 'mean' # Tỷ lệ thành công
    }).reset_index()

    # Làm phẳng tên cột
    summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in summary.columns.values]
    
    # Gộp thông tin Best Vector vào bảng tóm tắt
    summary = pd.merge(summary, best_configs, on="Algorithm", how="left")

    summary_file = RESULTS_DIR / f"{DATASET_NAME}_parallel_summary_k{s_k}_l{s_l}_c{s_c}.csv"
    summary.to_csv(summary_file, index=False)
    print(f"💾 Bảng thống kê tổng hợp: {summary_file}")

    # Hiển thị nhanh
    print("\n📊 KẾT QUẢ TÓM TẮT (MEAN ± STD)")
    print("="*100)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    display_df = summary[['Algorithm', 'Best_Fitness_mean', 'Best_Fitness_std', 'Execution_Time_s_mean', 'Iterations_mean', 'Success_mean']].copy()
    display_df['Fitness'] = display_df.apply(lambda x: f"{x['Best_Fitness_mean']:.2f} ± {x['Best_Fitness_std']:.2f}", axis=1)
    display_df['Time(s)'] = display_df['Execution_Time_s_mean'].round(2)
    display_df['Avg Iter'] = display_df['Iterations_mean'].round(1)
    
    print(display_df[['Algorithm', 'Fitness', 'Time(s)', 'Avg Iter']].to_string(index=False))
    print("="*100)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()