# config.py
from pathlib import Path

# ==================== CẤU HÌNH CHUNG ====================
BASE_DIR = Path(__file__).parent.resolve()

# Dataset hiện tại
DATASET_NAME = "medical"

# QUAN TRỌNG: Tên cột chứa thuộc tính nhạy cảm cần bảo vệ
SENSITIVE_ATTRIBUTE = "PrimaryDiagnosis"

# Đường dẫn
DATA_DIR = BASE_DIR / "data" / DATASET_NAME
INPUT_FILE = DATA_DIR / f"{DATASET_NAME}.csv"
HIERARCHY_DIR = DATA_DIR / "hierarchies"

# Kết quả
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Train/test index
TRAIN_TEST_DIR = DATA_DIR
TRAIN_TEST_DIR.mkdir(exist_ok=True)

# ==================== THAM SỐ ====================
K_ANONYMITY = 5
L_DIVERSITY = 3      # Giá trị l mặc định
C_RECURSIVE = 3.0    # Giá trị c mặc định cho Recursive (c, l)-Diversity 

ARO_PARAMS = {
    "npop": 15,       # Số lượng quần thể
    "max_it": 50,     # Số vòng lặp tối đa
    "w": 50.0,         # Trọng số Info Loss
    "u": 1000.0,     # Trọng số Phạt (k và l violations) - Cần lớn để ưu tiên riêng tư
    "v": 100.0,       # Trọng số Accuracy
    "log_every": 1,   # Ghi log mỗi bao nhiêu vòng lặp
    "patience": 10    # Dừng sớm nếu không cải thiện
}

CLASSIFIER_PARAMS = {
    "n_estimators": 50,
    "max_depth": 10,
    "train_size": 0.8
}

RANDOM_STATE = 42