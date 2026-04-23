# main.py
from hierarchy_loader import HierarchyLoader
from aro_apo_optimizer import aro_apo_optimization
from utils import genetic_algorithm_optimization, pso_optimization
from classifier import calculate_ca
from config import (
    INPUT_FILE, HIERARCHY_DIR, RESULTS_DIR, ARO_PARAMS,
    DATASET_NAME, K_ANONYMITY, L_DIVERSITY, C_RECURSIVE, SENSITIVE_ATTRIBUTE
)
import logging
import time
import csv
import os
from collections import Counter
import math
import pandas as pd
import numpy as np

# Tắt log hệ thống cho gọn màn hình
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def analyze_and_suggest_params(input_file, sensitive_attr):
    """
    Phân tích sâu dữ liệu để gợi ý tham số tối ưu (Adaptive Parameter Suggestion).
    """
    if not os.path.exists(input_file):
        print(f"Lỗi: Không tìm thấy file {input_file}")
        return K_ANONYMITY, L_DIVERSITY, C_RECURSIVE

    sensitive_values = []
    total_rows = 0
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames
        target_col = sensitive_attr
        if sensitive_attr not in fieldnames:
            target_col = fieldnames[-1] 
        
        for row in reader:
            total_rows += 1
            if target_col in row:
                sensitive_values.append(row[target_col])

    # --- PHÂN TÍCH THỐNG KÊ ---
    counts = Counter(sensitive_values)
    unique_count = len(counts)
    if unique_count == 0: return 2, 2, 1.0
    
    sorted_counts = sorted(counts.values(), reverse=True)
    r1 = sorted_counts[0]
    
    print("\n" + "="*60)
    print(f"📊 PHÂN TÍCH DỮ LIỆU CHUYÊN SÂU: {DATASET_NAME}")
    print("="*60)
    print(f"- Tổng số dòng: {total_rows}")
    print(f"- Số giá trị nhạy cảm khác nhau: {unique_count}")

    if total_rows < 500: suggested_k = 2
    elif total_rows < 10000: suggested_k = 5
    else: suggested_k = 10
    
    suggested_l = 2
    for i in range(1, min(unique_count, 5)):
        coverage_contribution = sorted_counts[i] / total_rows
        if coverage_contribution > 0.01:
            suggested_l = i + 1
        else:
            break
    
    suggested_l = min(suggested_l, 4)
    if unique_count < suggested_l: suggested_l = unique_count
    if suggested_l > suggested_k: suggested_l = suggested_k

    tail_sum = sum(sorted_counts[suggested_l-1:])
    if tail_sum == 0: c_global = float(r1)
    else: c_global = r1 / tail_sum

    alpha = 2.5
    buffer = 1 + (alpha / math.sqrt(suggested_k))
    suggested_c = round(c_global * buffer, 2)
    if suggested_c < 1.1: suggested_c = 1.1

    print(f"💡 GỢI Ý: k={suggested_k}, l={suggested_l}, c={suggested_c}")
    return suggested_k, suggested_l, suggested_c

def get_user_input(prompt, default_val, data_type=int):
    while True:
        user_in = input(f"{prompt} [Mặc định {default_val}]: ").strip()
        if not user_in: return default_val
        try:
            val = data_type(user_in)
            if val <= 0: print("Giá trị phải > 0."); continue
            return val
        except ValueError: print(f"Sai định dạng.")

def run_optimization(algo_name, optimize_func, loader, k, l, c, **params):
    print(f"\n🚀 Đang chạy {algo_name}...")
    start = time.time()
    
    out_file = RESULTS_DIR / f"{DATASET_NAME}_{algo_name}_k{k}_l{l}_c{c}.csv"
    
    # Gọi thuật toán
    best_x, best_f, history, info_loss, k_viol, l_viol = optimize_func(
        hierarchy_loader=loader,
        input_file=INPUT_FILE,
        k=k, l=l, c=c,
        output_file=out_file,
        **params
    )
    
    # Tính thời điểm hội tụ (Convergence Iteration)
    # Tìm index của lần đầu tiên đạt giá trị best_f (hoặc min của history)
    try:
        if isinstance(history, np.ndarray):
            hist_list = history.tolist()
        else:
            hist_list = list(history)
            
        min_val = min(hist_list)
        conv_it = hist_list.index(min_val) + 1 # +1 vì index bắt đầu từ 0
    except ValueError:
        conv_it = "N/A"

    # Tính accuracy
    acc_before, acc_after, _ = calculate_ca(INPUT_FILE, out_file)
    elapsed = time.time() - start
    
    return {
        "Algorithm": algo_name,
        "Fitness": best_f,
        "Info Loss": info_loss,
        "Accuracy": acc_after,
        "Violations (K/L)": f"{k_viol} / {l_viol}",
        "Convergence (It)": conv_it,  # <--- THÊM CỘT NÀY
        "Time (s)": elapsed,
        "Best Config": str(best_x)
    }

if __name__ == "__main__":
    s_k, s_l, s_c = analyze_and_suggest_params(INPUT_FILE, SENSITIVE_ATTRIBUTE)

    print("\nNhập tham số (Nhấn Enter để dùng gợi ý):")
    k = get_user_input("Nhập k", s_k, int)
    l = get_user_input("Nhập l", s_l, int)
    c = get_user_input("Nhập c", s_c, float)

    loader = HierarchyLoader(HIERARCHY_DIR)
    
    results = []

    # 1. Chạy Hybrid ARO-APO
    res_aro = run_optimization("ARO-APO", aro_apo_optimization, loader, k, l, c, **ARO_PARAMS)
    results.append(res_aro)

    # 2. Chạy Genetic Algorithm
    res_ga = run_optimization("GA", genetic_algorithm_optimization, loader, k, l, c, **ARO_PARAMS)
    results.append(res_ga)

    # 3. Chạy PSO
    res_pso = run_optimization("PSO", pso_optimization, loader, k, l, c, **ARO_PARAMS)
    results.append(res_pso)

    # --- HIỂN THỊ SO SÁNH ---
    print("\n" + "="*100)
    print("🏆 BẢNG SO SÁNH HIỆU NĂNG THUẬT TOÁN")
    print("="*100)
    
    df_res = pd.DataFrame(results)
    
    # Sắp xếp lại thứ tự cột
    cols = ["Algorithm", "Fitness", "Convergence (It)", "Info Loss", "Accuracy", "Violations (K/L)", "Time (s)"]
    
    # In bảng đẹp
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df_res[cols].to_string(index=False))
    
    print("-" * 100)
    
    # Tìm thuật toán tốt nhất (ưu tiên Fitness thấp nhất, sau đó là thời gian chạy)
    best_algo = df_res.sort_values(by=["Fitness", "Time (s)"]).iloc[0]
    print(f"⭐ Thuật toán tốt nhất: {best_algo['Algorithm']}")
    print(f"   ► Fitness: {best_algo['Fitness']:.6f}")
    print(f"   ► Hội tụ tại vòng: {best_algo['Convergence (It)']}")
    print("="*100)