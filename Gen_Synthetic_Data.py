import pandas as pd
import numpy as np
import csv
import os
import random
from datetime import datetime, timedelta

# --- CẤU HÌNH ---
NUM_ROWS = 50000
DATASET_NAME = "medical"
OUTPUT_DIR = os.path.join("data", DATASET_NAME)
HIERARCHY_DIR = os.path.join(OUTPUT_DIR, "hierarchies")
DATA_FILE = os.path.join(OUTPUT_DIR, f"{DATASET_NAME}.csv")
SEED = 2025

# Quy tắc đặt tên file phân cấp để khớp với hierarchy_loader.py
# Format: medical_hierarchy_Age.csv
PREFIX_HIERARCHY = f"{DATASET_NAME}_hierarchy_" 

np.random.seed(SEED)
random.seed(SEED)

os.makedirs(HIERARCHY_DIR, exist_ok=True)
print(f"🚀 Đang khởi tạo bộ dữ liệu '{DATASET_NAME}' ({NUM_ROWS} dòng)...")

# ==============================================================================
# PHẦN 1: ĐỊNH NGHĨA ONTOLOGY (CẤU TRÚC CÂY) - ĐỘ SÂU 4-7
# ==============================================================================

# 1. ĐỊA LÝ (Depth 6): Hamlets -> Wards -> Districts -> Provinces -> Regions -> Country
geo_ontology = {
    'Vietnam': {
        'Bac Bo': {
            'Ha Noi': {
                'Ba Dinh': {
                    'Phuc Xa': ['To 1', 'To 2'],
                    'Doi Can': ['Khu A', 'Khu B']
                },
                'Cau Giay': {
                    'Dich Vong': ['Lang Quoc Te', 'Khu Cong Vien'],
                    'Yen Hoa': ['To Dan Pho 3', 'To Dan Pho 4']
                }
            },
            'Quang Ninh': {
                'Ha Long': {
                    'Bai Chay': ['Khu Du Lich', 'Khu Dan Cu 1'],
                    'Hong Gai': ['Khu Ben Pha', 'Khu Cho']
                }
            }
        },
        'Nam Bo': {
            'Ho Chi Minh': {
                'Quan 1': {
                    'Ben Nghe': ['Khu Dong Khoi', 'Khu Le Thanh Ton'],
                    'Da Kao': ['Khu Phan Dinh Phung', 'Khu Dinh Tien Hoang']
                },
                'Binh Thanh': {
                    'Phuong 25': ['Khu D1', 'Khu D2'],
                    'Phuong 19': ['Khu Thi Nghe', 'Khu Pham Viet Chanh']
                }
            },
            'Can Tho': {
                'Ninh Kieu': {
                    'Tan An': ['Ben Ninh Kieu', 'Cho Dem'],
                    'Xuan Khanh': ['Khu Dai Hoc', 'Khu Bo Ke']
                }
            }
        }
    }
}

# 2. NGHỀ NGHIỆP (Depth 5): Job -> Sub-Dept -> Dept -> Sector -> Industry
job_ontology = {
    'Cong Nghiep': {
        'CNTT': {
            'Phan Mem': {
                'Backend': ['Java Dev', 'Python Dev', 'Go Dev'],
                'Frontend': ['React Dev', 'Vue Dev', 'Angular Dev']
            },
            'Ha Tang': {
                'Mang': ['Network Admin', 'Cisco Engineer'],
                'Cloud': ['AWS Architect', 'Azure Specialist']
            }
        },
        'San Xuat': {
            'Lap Rap': {
                'O To': ['Tho Han', 'Tho Son'],
                'Dien Tu': ['KCS', 'Tho Lap Mach']
            }
        }
    },
    'Dich Vu': {
        'Tai Chinh': {
            'Ngan Hang': {
                'Tin Dung': ['Chuyen Vien Tin Dung', 'Tham Dinh Vien'],
                'Giao Dich': ['Giao Dich Vien', 'Kiem Soat Vien']
            }
        },
        'Y Te': {
            'Lam Sang': {
                'Noi Khoa': ['Bac Si Tim Mach', 'Bac Si Tieu Hoa'],
                'Ngoai Khoa': ['Bac Si Gay Me', 'Bac Si Phau Thuat']
            }
        }
    }
}

# 3. DÂN TỘC (Depth 4): SubGroup -> Group -> Family -> Region
eth_ontology = {
    'Vietic': {
        'Viet-Muong': {
            'Kinh': ['Nguoi Kinh Bac', 'Nguoi Kinh Nam'],
            'Muong': ['Muong Bi', 'Muong Vang']
        }
    },
    'Tai-Kadai': {
        'Tai': {
            'Thai': ['Thai Den', 'Thai Trang'],
            'Tay': ['Tay Nung', 'Tay Khao']
        }
    },
    'Austronesian': {
        'Malayo-Polynesian': {
            'Cham': ['Cham Ba La Mon', 'Cham Ba Ni'],
            'E De': ['E De Kpa', 'E De Adham']
        }
    }
}

# 4. TRÌNH ĐỘ HỌC VẤN (Depth 4): Major -> Faculty -> Degree -> Level
edu_ontology = {
    'Dai Hoc & Sau DH': {
        'Cu Nhan': {
            'Ky Thuat': ['Ky Su CNTT', 'Ky Su Co Khi'],
            'Kinh Te': ['Cu Nhan QTKD', 'Cu Nhan Ke Toan']
        },
        'Thac Si': {
            'Khoa Hoc': ['Thac Si Khoa Hoc DL', 'Thac Si Toan'],
            'Quan Tri': ['MBA', 'Thac Si Quan Ly Cong']
        }
    },
    'Pho Thong': {
        'THPT': {
            'Chuyen': ['Chuyen Toan', 'Chuyen Ly'],
            'Thuong': ['Lop Chon', 'Lop Dai Tra']
        }
    }
}

# 5. BỆNH NỀN (QI) - ICD10 (Depth 5)
disease_ontology = {
    'Tuan Hoan': {
        'Tang Huyet Ap': {
            'Vo Can': ['I10 - Cao huyet ap vo can'],
            'Co Benh Tim': ['I11 - Benh tim do cao huyet ap']
        },
        'Thieu Mau Co Tim': {
            'Dau That Nguc': ['I20 - Con dau that nguc'],
            'Nhoi Mau': ['I21 - Nhoi mau co tim cap']
        }
    },
    'Ho Hap': {
        'Nhiem Trung': {
            'Cum': ['J10 - Cum do virus', 'J11 - Cum chua xac dinh'],
            'Viem Phoi': ['J12 - Viem phoi virus', 'J15 - Viem phoi vi khuan']
        }
    }
}

# ==============================================================================
# PHẦN 2: CÁC HÀM SINH FILE PHÂN CẤP
# ==============================================================================

def generate_hierarchy_recursive(node, current_path, rows, leaves):
    if isinstance(node, list): # Đã đến lá
        for leaf in node:
            # Format: Leaf; Parent; GrandParent; ...; Root; *
            full_hierarchy = [leaf] + current_path[::-1] + ["*"]
            rows.append(full_hierarchy)
            leaves.append(leaf)
        return

    for key, value in node.items():
        generate_hierarchy_recursive(value, current_path + [key], rows, leaves)

def create_categorical_hierarchy(ontology, attr_name):
    rows = []
    leaves = []
    generate_hierarchy_recursive(ontology, [], rows, leaves)
    
    filename = f"{PREFIX_HIERARCHY}{attr_name}.csv"
    filepath = os.path.join(HIERARCHY_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerows(rows)
        
    print(f"   ✅ {filename:<35} | Depth: {len(rows[0])} | Leaves: {len(leaves)}")
    return leaves

# --- GENERATORS SỐ HỌC (NUMERICAL / DATE) ---

def create_age_hierarchy():
    # Age -> 3y -> 5y -> 10y -> Gen -> *
    rows = []
    leaves = []
    for age in range(1, 101):
        age_str = str(age)
        lvl1 = f"{(age//3)*3}-{(age//3)*3+2}"
        lvl2 = f"{(age//5)*5}-{(age//5)*5+4}"
        lvl3 = f"{(age//10)*10}-{(age//10)*10+9}"
        lvl4 = "Gen Z" if age < 25 else ("Millennials" if age < 40 else ("Gen X" if age < 60 else "Boomers"))
        
        rows.append([age_str, lvl1, lvl2, lvl3, lvl4, "*"])
        leaves.append(age_str)
    
    filename = f"{PREFIX_HIERARCHY}Age.csv"
    with open(os.path.join(HIERARCHY_DIR, filename), 'w', newline='') as f:
        csv.writer(f, delimiter=';').writerows(rows)
    print(f"   ✅ {filename:<35} | Depth: {len(rows[0])}")
    return leaves

def create_date_hierarchy(attr_name, start_year=2010):
    # DD/MM/YYYY -> W/YYYY -> MM/YYYY -> Q/YYYY -> YYYY -> *
    rows = []
    leaves = []
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(2023, 12, 31)
    delta = end_date - start_date
    
    for i in range(delta.days + 1):
        day = start_date + timedelta(days=i)
        date_str = day.strftime("%d/%m/%Y")
        
        week = day.isocalendar()[1]
        yyyy = str(day.year)
        
        lvl1 = f"W{week}/{yyyy}"
        lvl2 = day.strftime("%m/%Y")
        lvl3 = f"Q{(day.month-1)//3 + 1}/{yyyy}"
        lvl4 = yyyy
        
        rows.append([date_str, lvl1, lvl2, lvl3, lvl4, "*"])
        leaves.append(date_str)

    filename = f"{PREFIX_HIERARCHY}{attr_name}.csv"
    with open(os.path.join(HIERARCHY_DIR, filename), 'w', newline='') as f:
        csv.writer(f, delimiter=';').writerows(rows)
    print(f"   ✅ {filename:<35} | Depth: {len(rows[0])}")
    return leaves

def create_income_hierarchy():
    # Exact -> Range 5M -> Range 10M -> Level -> *
    rows = []
    leaves = []
    for x in range(5, 101): 
        val = f"{x}M"
        lvl1 = f"{(x//5)*5}-{(x//5)*5+4}M"
        lvl2 = f"{(x//10)*10}-{(x//10)*10+9}M"
        lvl3 = "Thap" if x < 15 else ("Trung Binh" if x < 40 else "Cao")
        
        rows.append([val, lvl1, lvl2, lvl3, "*"])
        leaves.append(val)
    
    filename = f"{PREFIX_HIERARCHY}Income.csv"
    with open(os.path.join(HIERARCHY_DIR, filename), 'w', newline='') as f:
        csv.writer(f, delimiter=';').writerows(rows)
    print(f"   ✅ {filename:<35} | Depth: {len(rows[0])}")
    return leaves

# ==============================================================================
# PHẦN 3: SINH DỮ LIỆU
# ==============================================================================

print("\n--- BƯỚC 1: TẠO FILE PHÂN CẤP ---")

# 1. Sinh tập lá (Leaves) cho các thuộc tính Categorical
leaves_birthplace = create_categorical_hierarchy(geo_ontology, "BirthPlace")
# CurrentAddress dùng chung ontology với BirthPlace, ta copy hierarchy
import shutil
shutil.copy(os.path.join(HIERARCHY_DIR, f"{PREFIX_HIERARCHY}BirthPlace.csv"), 
            os.path.join(HIERARCHY_DIR, f"{PREFIX_HIERARCHY}CurrentAddress.csv"))
leaves_currentaddress = leaves_birthplace # Dùng chung list lá

leaves_job = create_categorical_hierarchy(job_ontology, "Job")
leaves_ethnicity = create_categorical_hierarchy(eth_ontology, "Ethnicity")
leaves_education = create_categorical_hierarchy(edu_ontology, "Education")
leaves_bg_disease = create_categorical_hierarchy(disease_ontology, "BackgroundDisease")

# 2. Sinh tập lá cho Numerical/Date
leaves_age = create_age_hierarchy()
leaves_dob = create_date_hierarchy("BirthDate", 1950)
leaves_adm_date = create_date_hierarchy("AdmissionDate", 2020)
leaves_dis_date = create_date_hierarchy("DischargeDate", 2020)
leaves_income = create_income_hierarchy()

# 3. Các thuộc tính đơn giản (Gender, MaritalStatus...)
# Tự tạo file hierarchy thủ công cho chúng
simple_attrs = {
    "Gender": ["Nam", "Nu"],
    "MaritalStatus": ["Doc than", "Da ket hon", "Ly hon"],
    "BloodType": ["A", "B", "AB", "O"],
    "ServiceType": ["BHYT", "Tu nguyen", "Vip"],
    "HospitalDept": ["Khoa Noi", "Khoa Ngoai", "Cap Cuu"]
}
leaves_simple = {}
for attr, vals in simple_attrs.items():
    rows = [[v, "*"] for v in vals]
    fname = f"{PREFIX_HIERARCHY}{attr}.csv"
    with open(os.path.join(HIERARCHY_DIR, fname), 'w', newline='') as f:
        csv.writer(f, delimiter=';').writerows(rows)
    leaves_simple[attr] = vals
    print(f"   ✅ {fname:<35} | Depth: 2")

print(f"\n--- BƯỚC 2: TẠO DỮ LIỆU ({NUM_ROWS} dòng) ---")

data = []
for _ in range(NUM_ROWS):
    row = {}
    
    # --- 1. NHÂN KHẨU HỌC ---
    row['BirthPlace'] = np.random.choice(leaves_birthplace)
    # 70% sống ở nơi sinh, 30% di cư
    if np.random.rand() < 0.7:
        row['CurrentAddress'] = row['BirthPlace']
    else:
        row['CurrentAddress'] = np.random.choice(leaves_currentaddress)
        
    row['Age'] = np.random.choice(leaves_age)
    row['Gender'] = np.random.choice(leaves_simple['Gender'])
    row['Ethnicity'] = np.random.choice(leaves_ethnicity)
    row['MaritalStatus'] = np.random.choice(leaves_simple['MaritalStatus'])
    row['BirthDate'] = np.random.choice(leaves_dob) # Lưu ý: Logic ngày sinh khớp tuổi bỏ qua để đơn giản

    # --- 2. KINH TẾ - XÃ HỘI ---
    row['Job'] = np.random.choice(leaves_job)
    row['Education'] = np.random.choice(leaves_education)
    row['Income'] = np.random.choice(leaves_income)
    
    # --- 3. Y TẾ / HÀNH CHÍNH ---
    row['AdmissionDate'] = np.random.choice(leaves_adm_date)
    row['DischargeDate'] = np.random.choice(leaves_dis_date)
    row['BloodType'] = np.random.choice(leaves_simple['BloodType'])
    row['ServiceType'] = np.random.choice(leaves_simple['ServiceType'])
    row['HospitalDept'] = np.random.choice(leaves_simple['HospitalDept'])
    row['BackgroundDisease'] = np.random.choice(leaves_bg_disease) # Bệnh nền (QI)
    
    # ID Bảo hiểm (QI dạng chuỗi)
    row['InsuranceID'] = f"BH-{np.random.randint(1000,9999)}" 
    # Cần tạo hierarchy cho ID này (Dummy)
    # Ở đây ta bỏ qua tạo file hierarchy cho ID vì quá nhiều giá trị unique,
    # Nếu chạy code sẽ cần file InsuranceID_hierarchy... csv.
    # Để code chạy được, ta gán ID về một nhóm chung trong data mẫu này hoặc không dùng làm QI.
    # Sửa: Để đơn giản, ta dùng InsuranceGroup thay vì ID unique
    row['InsuranceGroup'] = np.random.choice(["Group_A", "Group_B", "Group_C"])

    # --- 4. SENSITIVE ATTRIBUTE (BỆNH LÝ CHÍNH) ---
    # Tương quan dữ liệu: Tuổi cao, Bệnh nền -> Bệnh nặng
    age_int = int(row['Age'])
    bg_dis = row['BackgroundDisease']
    
    probs = [0.25, 0.25, 0.25, 0.25] # Ung thu, Tieu duong, Sot xuat huyet, Dot quy
    
    if age_int > 50 or 'Cao huyet ap' in bg_dis:
        probs = [0.2, 0.2, 0.05, 0.55] # Nguy cơ Đột quỵ cao
    
    row['PrimaryDiagnosis'] = np.random.choice(['Ung Thu Phoi', 'Tieu Duong Type 2', 'Sot Xuat Huyet', 'Dot Quy'], p=probs)
    
    data.append(row)

# Tạo file hierarchy cho cột InsuranceGroup vừa thêm
with open(os.path.join(HIERARCHY_DIR, f"{PREFIX_HIERARCHY}InsuranceGroup.csv"), 'w', newline='') as f:
    csv.writer(f, delimiter=';').writerows([[g, "*"] for g in ["Group_A", "Group_B", "Group_C"]])

# Lưu file CSV
df = pd.DataFrame(data)
cols = [
    'AdmissionDate', 'DischargeDate', 'BirthDate', 
    'BirthPlace', 'CurrentAddress', 'Age', 'Gender', 'Ethnicity', 
    'MaritalStatus', 'Job', 'Education', 'Income', 
    'BloodType', 'ServiceType', 'HospitalDept', 'InsuranceGroup', 
    'BackgroundDisease', 
    'PrimaryDiagnosis' # SENSITIVE
]
df = df[cols]
df.to_csv(DATA_FILE, index=False, sep=';', encoding='utf-8')

print(f"✅ ĐÃ XONG! File dữ liệu: {DATA_FILE}")
print(f"📂 Thư mục chứa {len(os.listdir(HIERARCHY_DIR))} file phân cấp: {HIERARCHY_DIR}")