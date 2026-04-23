# visualize_pro.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import ast
import config

sns.set_theme(style="whitegrid", context="paper", font_scale=1.5)
plt.rcParams['font.family'] = 'serif'
RESULTS_DIR = config.RESULTS_DIR

def load_data():
    raw_files = list(RESULTS_DIR.glob("MASTER_RAW_6_DATASETS.csv")) # Ưu tiên file gộp 6 bộ
    if not raw_files: 
        raw_files = list(RESULTS_DIR.glob("MASTER_RAW_*.csv"))
        
    if raw_files:
        latest = max(raw_files, key=lambda f: f.stat().st_mtime)
        print(f"📖 Đọc file: {latest.name}")
        return pd.read_csv(latest)
    return None

def draw_separate_boxplots(df, metric, ylabel, prefix):
    """Vẽ Boxplot từng bộ riêng biệt cho đẹp"""
    for ds in df['Dataset'].unique():
        subset = df[df['Dataset'] == ds]
        plt.figure(figsize=(8, 6))
        
        sns.boxplot(data=subset, x="Algorithm", y=metric, palette="Set2", width=0.5, showfliers=False)
        sns.stripplot(data=subset, x="Algorithm", y=metric, size=4, color=".3", alpha=0.5, jitter=True)

        plt.title(f"{ds.upper()} - {ylabel}", fontweight='bold')
        plt.ylabel(ylabel); plt.xlabel("")
        plt.tight_layout()
        plt.savefig(RESULTS_DIR / f"{prefix}_{ds}.png", dpi=300)
        plt.close()
    print(f"✅ Đã vẽ xong Boxplot cho {prefix}")

def draw_convergence_line(df):
    """
    Vẽ biểu đồ hội tụ với cơ chế Padding (Kéo dài) cho thuật toán dừng sớm.
    """
    if 'Fitness_History' not in df.columns: return

    print("📈 Đang vẽ biểu đồ đường hội tụ (với Padding)...")
    
    # Duyệt qua từng bộ dữ liệu
    for ds in df['Dataset'].unique():
        ds_data = df[df['Dataset'] == ds]
        
        # 1. Tìm độ dài lớn nhất (Max Iteration) trong toàn bộ thuật toán của dataset này
        # Để đảm bảo trục X của mọi đường đều dài bằng nhau (ví dụ: đều là 50)
        global_max_len = 0
        all_histories = {} # Lưu lại để đỡ phải parse 2 lần

        for algo in ds_data['Algorithm'].unique():
            algo_data = ds_data[ds_data['Algorithm'] == algo]
            parsed_hists = []
            for h_str in algo_data['Fitness_History']:
                try:
                    h_list = ast.literal_eval(str(h_str))
                    if isinstance(h_list, list) and len(h_list) > 0:
                        parsed_hists.append(h_list)
                        global_max_len = max(global_max_len, len(h_list))
                except: pass
            all_histories[algo] = parsed_hists
        
        if global_max_len == 0: continue # Không có dữ liệu history nào

        # 2. Bắt đầu vẽ
        plt.figure(figsize=(10, 6))
        
        colors = {"ARO-APO": "red", "GA": "blue", "PSO": "green"}
        styles = {"ARO-APO": "-", "GA": "--", "PSO": "-."}
        markers = {"ARO-APO": "o", "GA": "s", "PSO": "^"} # Thêm marker cho dễ phân biệt

        for algo, histories in all_histories.items():
            if not histories: continue
            
            # --- KỸ THUẬT PADDING (LẤP ĐẦY) ---
            # Nếu history ngắn hơn global_max_len, lấy giá trị cuối cùng đắp vào đuôi
            padded_histories = []
            for h in histories:
                current_len = len(h)
                if current_len < global_max_len:
                    # Copy phần tử cuối cùng thêm (max - current) lần
                    extended_h = h + [h[-1]] * (global_max_len - current_len)
                    padded_histories.append(extended_h)
                else:
                    padded_histories.append(h)
            
            # Tính trung bình (Mean Curve)
            arr = np.array(padded_histories)
            mean_curve = np.mean(arr, axis=0)
            
            # Tạo trục X
            x_axis = range(1, global_max_len + 1)
            
            # Vẽ đường
            # markevery: Chỉ hiện marker mỗi 5 điểm để đỡ rối mắt
            plt.plot(
                x_axis, 
                mean_curve, 
                label=algo, 
                color=colors.get(algo, 'black'),
                linestyle=styles.get(algo, '-'),
                linewidth=2,
                marker=markers.get(algo, ''),
                markevery=int(global_max_len/10) + 1, 
                markersize=6
            )

        plt.title(f"{ds.upper()} - Convergence Speed Analysis", fontweight='bold', pad=15)
        plt.xlabel("Iteration", fontweight='bold')
        plt.ylabel("Best Fitness (Log Scale)", fontweight='bold')
        plt.yscale('log') # Log scale để nhìn rõ sự giảm fitness ban đầu
        plt.legend()
        plt.grid(True, which="major", ls="--", alpha=0.6)
        plt.grid(True, which="minor", ls=":", alpha=0.3)
        
        filename = f"Line_Convergence_{ds}.png"
        save_path = RESULTS_DIR / filename
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        print(f"   ✅ Đã vẽ: {filename} (Max Iter: {global_max_len})")
        plt.close()

def main():
    df = load_data()
    if df is None: return
    
    # Vẽ Boxplot (Vẽ cho TẤT CẢ dataset)
    draw_separate_boxplots(df, "Best_Fitness", "Fitness Value", "Boxplot_Fitness")
    draw_separate_boxplots(df, "Accuracy_After", "Accuracy", "Boxplot_Accuracy")
    
    # Vẽ Line Chart (Chỉ vẽ cho MEDICAL hoặc bộ nào có History)
    draw_convergence_line(df)

if __name__ == "__main__":
    main()