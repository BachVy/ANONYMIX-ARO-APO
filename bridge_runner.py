# bridge_runner.py
import sys
import run_batch
import update_results_logic
import os

# Ép hệ thống xuất dữ liệu theo chuẩn UTF-8 ngay từ đầu
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing dataset name argument.")
        sys.exit(1)
        
    dataset_name = sys.argv[1]
    
    # Dùng tiếng Anh để tuyệt đối không bị lỗi Encoding khi truyền dữ liệu qua Pipe
    print(f"--- [BRIDGE] Starting experiment for: {dataset_name} ---")
    
    try:
        # 1. Chạy thuật toán chính
        res_df = run_batch.run_dataset_experiment(dataset_name)
        
        if res_df is not None:
            print(f"--- [BRIDGE] Success! Data collected for {dataset_name}. ---")
            
            # 2. Gộp kết quả và vẽ biểu đồ
            print("--- [BRIDGE] Updating reports and charts... ---")
            update_results_logic.update_all_reports(dataset_name, res_df)
            
            print("--- [BRIDGE] ALL PROCESSES COMPLETED ---")
        else:
            print("--- [BRIDGE] Error: Experiment returned None. ---")
            sys.exit(1)
            
    except Exception as e:
        print(f"--- [BRIDGE] CRITICAL ERROR: {str(e)} ---")
        sys.exit(1)