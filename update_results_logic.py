# update_results_logic.py
import pandas as pd
import config
from pathlib import Path
import numpy as np

def update_all_reports(current_dataset=None, current_df=None):
    """
    Hàm xử lý: 
    1. Lưu kết quả của dataset vừa chạy xong.
    2. Gộp tất cả kết quả cũ + mới từ ổ cứng.
    3. Cập nhật biểu đồ và bảng biểu.
    """
    print("\n" + "="*80)
    print("🔄 TIẾN TRÌNH TỔNG HỢP DỮ LIỆU (CŨ + MỚI)")
    print("="*80)

    # BƯỚC 1: LƯU KẾT QUẢ RIÊNG CỦA DATASET VỪA CHẠY (Nếu có)
    if current_dataset and current_df is not None:
        temp_save = config.RESULTS_DIR / f"TEMP_RES_{current_dataset}.csv"
        current_df.to_csv(temp_save, index=False)
        print(f"💾 1. Đã lưu tạm kết quả mới cho: {current_dataset}")

    # BƯỚC 2: QUÉT VÀ GỘP TẤT CẢ TỪ Ổ CỨNG
    # Danh sách đầy đủ các bộ dữ liệu mục tiêu
    FULL_DATASET_LIST = ["italia", "cmc", "mgm", "cahousing", "adult", "informs", "medical"]
    final_collection = []
    
    print("📥 2. Đang nạp dữ liệu tích lũy...")
    for ds_name in FULL_DATASET_LIST:
        temp_file = config.RESULTS_DIR / f"TEMP_RES_{ds_name}.csv"
        
        if temp_file.exists():
            try:
                df_temp = pd.read_csv(temp_file)
                # Xử lý tương thích nếu thiếu cột History
                if 'Fitness_History' not in df_temp.columns:
                    df_temp['Fitness_History'] = np.nan
                final_collection.append(df_temp)
                print(f"   ✅ Đã nạp: {ds_name}")
            except Exception as e:
                print(f"   ❌ Lỗi khi đọc {ds_name}: {e}")
        else:
            print(f"   ⚠️ Trống: {ds_name} (Chưa có kết quả)")

    if not final_collection:
        print("❌ Không tìm thấy dữ liệu nào để tổng hợp.")
        return

    # BƯỚC 3: XUẤT FILE MASTER TỔNG HỢP
    final_df = pd.concat(final_collection, ignore_index=True)
    
    # 1. Lưu Raw Data (Đủ các bộ đã chạy)
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
    
    summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in summary.columns.values]
    summary_path = config.RESULTS_DIR / "MASTER_SUMMARY_ALL_DATASETS.csv"
    summary.to_csv(summary_path, index=False)
    
    print(f"🏆 3. Hoàn tất gộp {len(final_collection)} bộ dữ liệu.")
    print(f"📁 File tổng hợp: {summary_path.name}")

    # BƯỚC 4: TỰ ĐỘNG VẼ BIỂU ĐỒ VÀ TẠO BẢNG CHUẨN BÁO CÁO
    print("\n📊 4. Đang cập nhật biểu đồ và bảng báo cáo...")
    try:
        import ve_all
        import visualize
        import create_report_table
        
        ve_all.main()             # Cập nhật biểu đồ tổng hợp
        visualize.main()          # Cập nhật biểu đồ chi tiết từng bộ
        create_report_table.main() # Cập nhật 3 bảng CSV chuẩn (Mean ± Std)
        print("✅ Báo cáo đã được làm mới hoàn toàn!")
    except Exception as e:
        print(f"⚠️ Lỗi khi cập nhật hình ảnh: {e}")

    print("="*80 + "\n")


