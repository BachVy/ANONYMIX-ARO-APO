# merge_results.py
import pandas as pd
import config
import numpy as np

# Danh sách 5 bộ cũ (đã xong) + 1 bộ mới (medical)
TARGET_DATASETS = ["italia", "cmc", "mgm", "cahousing", "adult", "medical"]

def main():
    print("🚀 ĐANG GỘP DỮ LIỆU CŨ VÀ MỚI...")
    final_collection = []
    
    for ds_name in TARGET_DATASETS:
        temp_file = config.RESULTS_DIR / f"TEMP_RES_{ds_name}.csv"
        if temp_file.exists():
            df = pd.read_csv(temp_file)
            # Nếu là bộ cũ chưa có cột Fitness_History, ta tạo cột rỗng để không bị lỗi khi gộp
            if 'Fitness_History' not in df.columns:
                df['Fitness_History'] = np.nan 
            final_collection.append(df)
            print(f"✅ Đã nạp: {ds_name}")
        else:
            print(f"⚠️ Thiếu file: {ds_name}")

    if not final_collection: return

    # Gộp và Lưu
    final_df = pd.concat(final_collection, ignore_index=True)
    final_df.to_csv(config.RESULTS_DIR / "MASTER_RAW_6_DATASETS.csv", index=False)
    
    # Tính toán bảng tổng hợp (bỏ qua cột History khi tính mean)
    summary = final_df.groupby(['Dataset', 'Algorithm']).agg({
        'Best_Fitness': ['mean', 'std'],
        'Accuracy_After': ['mean', 'std'],
        'Execution_Time_s': ['mean', 'std'],
        'Iterations': ['mean'],
        'Success': ['mean']
    }).reset_index()
    
    summary.columns = ['_'.join(col).strip() if col[1] else col[0] for col in summary.columns.values]
    summary.to_csv(config.RESULTS_DIR / "MASTER_SUMMARY_6_DATASETS.csv", index=False)
    print("🏆 XONG! Đã có file MASTER_RAW_6_DATASETS.csv")

if __name__ == '__main__':
    main()