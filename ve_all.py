# visualize_all_in_one.py
import matplotlib
matplotlib.use('Agg') # ÉP BUỘC CHẾ ĐỘ CHẠY NGẦM (NON-INTERACTIVE)
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast
import math
import config

# Cấu hình giao diện
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
plt.rcParams['font.family'] = 'serif'

RESULTS_DIR = config.RESULTS_DIR

def load_data():
    """Tìm file kết quả gộp mới nhất"""
    # Ưu tiên file gộp 6 bộ hoặc file gộp all
    files = list(RESULTS_DIR.glob("MASTER_RAW_*.csv"))
    if files:
        latest = max(files, key=lambda f: f.stat().st_mtime)
        print(f"📖 Đang đọc file: {latest.name}")
        return pd.read_csv(latest)
    print("❌ Không tìm thấy file dữ liệu MASTER_RAW nào!")
    return None

def plot_combined_boxplot(df, metric, ylabel, filename, log_scale=False):
    """
    Vẽ Boxplot gộp:
    - Trục X: Các bộ dữ liệu (Medical, Italia...)
    - Màu sắc (Hue): Các thuật toán (ARO, GA, PSO)
    """
    plt.figure(figsize=(16, 8)) # Khung hình rộng
    
    # Vẽ Boxplot
    ax = sns.boxplot(
        data=df,
        x="Dataset",
        y=metric,
        hue="Algorithm",
        palette="viridis",
        width=0.7,
        linewidth=1.2,
        showfliers=False # Ẩn điểm ngoại lai để hình đỡ bị nén
    )
    
    # Tùy chỉnh
    if log_scale:
        ax.set_yscale("log")
        ylabel += " (Log Scale)"

    plt.title(f"Comparison of {ylabel} across all Datasets", fontsize=18, fontweight='bold', pad=20)
    plt.ylabel(ylabel, fontweight='bold', fontsize=14)
    plt.xlabel("Dataset", fontweight='bold', fontsize=14)
    plt.xticks(rotation=0, fontweight='bold', fontsize=12) # Tên dataset nằm ngang
    plt.legend(title="Algorithm", loc='upper right', frameon=True)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    save_path = RESULTS_DIR / f"{filename}.png"
    plt.savefig(save_path, dpi=300)
    print(f"🖼️  Đã lưu Boxplot gộp: {filename}.png")
    plt.close()

def plot_grid_convergence(df):
    """
    Vẽ biểu đồ đường dạng LƯỚI (Grid Subplots).
    Tự động tính toán số hàng/cột dựa trên số lượng dataset.
    """
    if 'Fitness_History' not in df.columns: return

    datasets = df['Dataset'].unique()
    n_ds = len(datasets)
    
    # Tính số cột và dòng (Ví dụ 6 dataset -> 2 dòng, 3 cột)
    n_cols = 3
    n_rows = math.ceil(n_ds / n_cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(18, 5 * n_rows))
    axes = axes.flatten() # Làm phẳng mảng axes để dễ duyệt vòng lặp

    colors = {"ARO-APO": "red", "GA": "blue", "PSO": "green"}
    styles = {"ARO-APO": "-", "GA": "--", "PSO": "-."}
    
    print("📈 Đang vẽ biểu đồ lưới hội tụ...")

    for i, ds in enumerate(datasets):
        ax = axes[i]
        ds_data = df[df['Dataset'] == ds]
        
        # --- Logic xử lý Padding (như cũ) ---
        global_max_len = 0
        all_histories = {}
        for algo in ds_data['Algorithm'].unique():
            algo_data = ds_data[ds_data['Algorithm'] == algo]
            parsed = []
            for h_str in algo_data['Fitness_History']:
                try:
                    h = ast.literal_eval(str(h_str))
                    if isinstance(h, list) and h: 
                        parsed.append(h)
                        global_max_len = max(global_max_len, len(h))
                except: pass
            all_histories[algo] = parsed
        
        # --- Vẽ lên trục ax nhỏ ---
        if global_max_len > 0:
            for algo, histories in all_histories.items():
                if not histories: continue
                padded = []
                for h in histories:
                    if len(h) < global_max_len:
                        padded.append(h + [h[-1]] * (global_max_len - len(h)))
                    else:
                        padded.append(h)
                
                mean_curve = np.mean(np.array(padded), axis=0)
                x_axis = range(1, global_max_len + 1)
                
                ax.plot(x_axis, mean_curve, label=algo, 
                        color=colors.get(algo, 'k'), ls=styles.get(algo, '-'), lw=2)
            
            ax.set_yscale('log') # Log scale cực quan trọng
            ax.set_title(ds.upper(), fontweight='bold', fontsize=14)
            ax.grid(True, linestyle='--', alpha=0.5)
            if i == 0: ax.legend() # Chỉ hiện chú thích ở hình đầu tiên cho đỡ rối

        else:
            ax.text(0.5, 0.5, "No History Data", ha='center', va='center')

    # Ẩn các ô thừa (nếu có, ví dụ 7 dataset vẽ trên lưới 3x3=9 ô)
    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.suptitle("Convergence Analysis Overview", fontsize=20, fontweight='bold', y=0.98)
    plt.tight_layout()
    
    save_path = RESULTS_DIR / "ALL_IN_ONE_Convergence.png"
    plt.savefig(save_path, dpi=300)
    print(f"🖼️  Đã lưu biểu đồ lưới: ALL_IN_ONE_Convergence.png")
    plt.close()


def main():
    df = load_data()
    if df is None: return

    # 1. Vẽ Accuracy chung 1 hình
    # Trục X là Dataset, Hue là Algorithm
    plot_combined_boxplot(df, "Accuracy_After", "Accuracy Score", "ALL_IN_ONE_Accuracy")

    # 2. Vẽ Fitness chung 1 hình (Dùng Log Scale vì chênh lệch lớn)
    plot_combined_boxplot(df, "Best_Fitness", "Fitness Value", "ALL_IN_ONE_Fitness", log_scale=True)
    
    # 3. Vẽ Time chung 1 hình
    plot_combined_boxplot(df, "Execution_Time_s", "Execution Time (s)", "ALL_IN_ONE_Time")

    # 4. Vẽ Convergence dạng lưới (Grid)
    plot_grid_convergence(df)

if __name__ == "__main__":
    main()