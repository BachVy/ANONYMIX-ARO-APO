# create_report_table.py
import pandas as pd
import config
from pathlib import Path

# Cấu hình file đầu vào (Chọn file summary mới nhất của bạn)
# Nếu bạn chạy 6 bộ, nó sẽ tự tìm file 6 bộ. Nếu 7 bộ sẽ tìm file 7 bộ.
def get_latest_summary_file():
    files = list(config.RESULTS_DIR.glob("MASTER_SUMMARY_*.csv"))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)

def format_value(mean, std, format_str="{:.2f}"):
    """Hàm format số liệu thành dạng: Mean ± Std"""
    m = format_str.format(mean)
    s = format_str.format(std)
    return f"{m} ± {s}"

def main():
    input_file = get_latest_summary_file()
    if not input_file:
        print("❌ Không tìm thấy file MASTER_SUMMARY nào trong thư mục results/")
        return

    print(f"📖 Đang xử lý file: {input_file.name}")
    df = pd.read_csv(input_file)

    # 1. TẠO CÁC CỘT FORMAT CHUẨN (Mean ± Std)
    # Fitness
    df['Fitness (Mean±Std)'] = df.apply(
        lambda row: format_value(row['Best_Fitness_mean'], row['Best_Fitness_std'], "{:.4f}"), axis=1
    )
    
    # Accuracy
    df['Accuracy (Mean±Std)'] = df.apply(
        lambda row: format_value(row['Accuracy_After_mean'], row['Accuracy_After_std'], "{:.4f}"), axis=1
    )
    
    # Time
    df['Time (Mean±Std)'] = df.apply(
        lambda row: format_value(row['Execution_Time_s_mean'], row['Execution_Time_s_std'], "{:.2f}"), axis=1
    )

    # 2. XOAY BẢNG (PIVOT) ĐỂ COPY VÀO BÁO
    # Chúng ta sẽ tạo 3 bảng riêng biệt cho 3 chỉ số
    
    # --- Bảng 1: Fitness Comparison ---
    pivot_fitness = df.pivot(index='Dataset', columns='Algorithm', values='Fitness (Mean±Std)')
    pivot_fitness.to_csv(config.RESULTS_DIR / "TABLE_Fitness_Final.csv")
    
    # --- Bảng 2: Accuracy Comparison ---
    pivot_accuracy = df.pivot(index='Dataset', columns='Algorithm', values='Accuracy (Mean±Std)')
    pivot_accuracy.to_csv(config.RESULTS_DIR / "TABLE_Accuracy_Final.csv")
    
    # --- Bảng 3: Time Comparison ---
    pivot_time = df.pivot(index='Dataset', columns='Algorithm', values='Time (Mean±Std)')
    pivot_time.to_csv(config.RESULTS_DIR / "TABLE_Time_Final.csv")

    print("\n" + "="*80)
    print("✅ ĐÃ TẠO 3 BẢNG SỐ LIỆU CHUẨN FORMAT BÀI BÁO (DẠNG 50 ± 5)")
    print("="*80)
    print("1. TABLE_Fitness_Final.csv  -> Dùng cho Bảng so sánh hàm mất mát")
    print("2. TABLE_Accuracy_Final.csv -> Dùng cho Bảng so sánh độ chính xác")
    print("3. TABLE_Time_Final.csv     -> Dùng cho Bảng so sánh thời gian")
    print("\n💡 Gợi ý: Bạn mở file CSV bằng Excel, rồi copy thẳng vào Word/LaTeX.")

if __name__ == "__main__":
    main()