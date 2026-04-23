# anonymizer.py
import csv
import os
from collections import Counter, defaultdict
from config import SENSITIVE_ATTRIBUTE

class Anonymizer:
    def __init__(self, hierarchy_loader):
        self.hierarchy_loader = hierarchy_loader

    def is_recursive_cl_diverse(self, sensitive_values, l, c):
        """
        Kiểm tra tính chất Recursive (c, l)-Diversity.
        Định nghĩa: r1 < c * (rl + rl+1 + ... + rm)
        """
        # 1. Đếm tần suất
        counts = Counter(sensitive_values)
        
        # 2. Sắp xếp giảm dần: r = [r1, r2, ...]
        r = sorted(counts.values(), reverse=True)
        
        # 3. Kiểm tra số lượng giá trị khác biệt (m)
        if len(r) < l:
            return False
        
        # 4. Tính r1 và tổng đuôi (Tail Sum)
        r1 = r[0]
        # Python index bắt đầu từ 0, nên r_l nằm ở vị trí l-1
        tail_sum = sum(r[l-1:])
        
        # 5. Kiểm tra điều kiện
        if tail_sum == 0:
            return False
            
        return r1 < c * tail_sum

    def anonymize(self, generalization_levels, input_file, k, l=1, c=1.0, output_file=None):
        """
        Thực hiện ẩn danh và kiểm tra vi phạm.
        Trả về: rows, min_k_actual, k_violations, l_violations
        """
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"File không tồn tại: {input_file}")

        hierarchies = {
            attr: self.hierarchy_loader.load_hierarchy(attr, level)
            for attr, level in generalization_levels.items()
            if attr in self.hierarchy_loader.available_attributes
        }

        rows = []
        groups_sensitive = defaultdict(list)

        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            fieldnames = reader.fieldnames
            
            # Tìm cột nhạy cảm
            if SENSITIVE_ATTRIBUTE in fieldnames:
                sensitive_col = SENSITIVE_ATTRIBUTE
            else:
                sensitive_col = fieldnames[-1]

            for row in reader:
                anon_row = row.copy()
                for attr, mapping in hierarchies.items():
                    val = anon_row[attr].strip()
                    anon_row[attr] = mapping.get(val, val)
                
                rows.append(anon_row)
                group_key = tuple(anon_row[attr] for attr in hierarchies)
                groups_sensitive[group_key].append(anon_row[sensitive_col])

        # --- ĐÁNH GIÁ VI PHẠM ---
        k_violations = 0
        l_violations = 0
        min_k_actual = float('inf') if groups_sensitive else 0
        
        for key, sensitive_vals in groups_sensitive.items():
            group_size = len(sensitive_vals)
            
            if group_size < min_k_actual:
                min_k_actual = group_size
            
            # Kiểm tra K-Anonymity
            if group_size < k:
                k_violations += 1
            
            # Kiểm tra Recursive Diversity
            if group_size > 0:
                if not self.is_recursive_cl_diverse(sensitive_vals, l, c):
                    l_violations += 1

        # Xuất file kết quả
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(rows)

        return rows, min_k_actual, k_violations, l_violations