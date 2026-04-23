# classifier.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OrdinalEncoder
from config import CLASSIFIER_PARAMS, TRAIN_TEST_DIR, RANDOM_STATE
import os

def process_generalized_numeric(val):
    """Xử lý các giá trị dạng khoảng (10-20) hoặc sao (*) thành số"""
    if isinstance(val, str):
        val = val.strip()
        if '~' in val:
            try:
                a, b = map(float, val.split('~'))
                return (a + b) / 2
            except:
                return np.nan
        if '-' in val and len(val.split('-')) == 2: # Xử lý dạng 10-20
             try:
                a, b = map(float, val.split('-'))
                return (a + b) / 2
             except:
                 pass # Có thể là mã số dạng BH-123
        if val == '*' or val == '*****':
            return np.nan # Coi sao là missing value để điền trung bình
        try:
            return float(val)
        except:
            return val
    return val

def calculate_accuracy(file_path, save_split=False):
    # Đọc dữ liệu
    df = pd.read_csv(file_path, delimiter=';')
    
    # Tách X (features) và y (target - cột cuối cùng)
    X, y = df.iloc[:, :-1], df.iloc[:, -1]

    # Copy để xử lý
    X_proc = X.copy()
    
    # Phân loại cột số và cột chữ
    # Lưu ý: Cần kiểm tra kỹ vì sau khi ẩn danh, cột số có thể biến thành object (string)
    # Ta sẽ thử ép kiểu sang số, nếu thất bại nhiều thì coi là cột chữ (categorical)
    num_cols = []
    cat_cols = []
    
    for col in X_proc.columns:
        # Thử chuyển đổi sang số
        temp_col = X_proc[col].apply(process_generalized_numeric)
        # Nếu hơn 80% là số thực -> Coi là cột số
        n_numeric = pd.to_numeric(temp_col, errors='coerce').notna().sum()
        if n_numeric / len(temp_col) > 0.8:
            num_cols.append(col)
            X_proc[col] = pd.to_numeric(temp_col, errors='coerce')
        else:
            cat_cols.append(col)
            # Với cột chữ, chuyển hết về dạng string để tránh lỗi mixed types
            X_proc[col] = X_proc[col].astype(str)

    # 1. Xử lý cột SỐ: Điền giá trị thiếu bằng trung bình
    for col in num_cols:
        mean_val = X_proc[col].mean()
        X_proc[col] = X_proc[col].fillna(mean_val)

    # 2. Xử lý cột CHỮ: Dùng Ordinal Encoding (Thay vì One-Hot)
    # Đây là chìa khóa để sửa lỗi tràn RAM
    if len(cat_cols) > 0:
        # Unknown value = -1 để xử lý các giá trị lạ xuất hiện trong tập test
        enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
        
        # Fit và Transform
        X_cat_encoded = enc.fit_transform(X_proc[cat_cols])
        
        # Tạo DataFrame từ kết quả encode
        X_cat_df = pd.DataFrame(X_cat_encoded, columns=cat_cols, index=X_proc.index)
        
        # Ghép lại với cột số
        X_final = pd.concat([X_proc[num_cols], X_cat_df], axis=1)
    else:
        X_final = X_proc[num_cols]

    # Chia tập Train/Test (Giữ nguyên random_state=42 để ổn định)
    sss = StratifiedShuffleSplit(n_splits=1, 
                                 train_size=CLASSIFIER_PARAMS['train_size'], 
                                 random_state=RANDOM_STATE)
    
    try:
        train_idx, test_idx = next(sss.split(X_final, y))
    except ValueError:
        # Fallback nếu Stratified thất bại (do y chỉ có 1 class chẳng hạn)
        from sklearn.model_selection import ShuffleSplit
        ss = ShuffleSplit(n_splits=1, train_size=CLASSIFIER_PARAMS['train_size'], random_state=RANDOM_STATE)
        train_idx, test_idx = next(ss.split(X_final, y))

    X_train, X_test = X_final.iloc[train_idx], X_final.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    # Lưu vết index (chỉ làm khi chạy file gốc)
    if save_split:
        name = os.path.splitext(os.path.basename(file_path))[0]
        with open(TRAIN_TEST_DIR / f"{name}_train.txt", 'w') as f:
            for i in train_idx: f.write(f"{i}\n")
        with open(TRAIN_TEST_DIR / f"{name}_test.txt", 'w') as f:
            for i in test_idx: f.write(f"{i}\n")

    # Huấn luyện Random Forest
    clf = RandomForestClassifier(
        n_estimators=CLASSIFIER_PARAMS['n_estimators'],
        max_depth=CLASSIFIER_PARAMS['max_depth'],
        random_state=RANDOM_STATE
    )
    clf.fit(X_train, y_train)
    
    return accuracy_score(y_test, clf.predict(X_test))

def calculate_ca(original_file, anonymized_file):
    acc_before = calculate_accuracy(original_file, save_split=True)
    acc_after = calculate_accuracy(anonymized_file)
    return acc_before, acc_after, acc_before - acc_after