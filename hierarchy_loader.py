# hierarchy_loader.py
import csv
import os
import glob
from config import HIERARCHY_DIR

class HierarchyLoader:
    def __init__(self, hierarchy_dir=None):
        self.hierarchy_dir = hierarchy_dir or HIERARCHY_DIR
        self.hierarchies = self._load_hierarchies()
        self.max_levels = self._compute_max_levels()
        self.available_attributes = list(self.hierarchies.keys())

    def _load_hierarchies(self):
        hierarchies = {}
        pattern = os.path.join(self.hierarchy_dir, "*_hierarchy_*.csv")
        csv_files = glob.glob(pattern)
        if not csv_files:
            raise FileNotFoundError(f"Không tìm thấy file hierarchy trong: {self.hierarchy_dir}")
        for csv_file in csv_files:
            attr = os.path.basename(csv_file).split("_hierarchy_")[1].replace(".csv", "")
            hierarchies[attr] = {}
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if row:
                        orig = row[0].strip()
                        levels = [lvl.strip() for lvl in row[1:] if lvl.strip()]
                        hierarchies[attr][orig] = levels
        return hierarchies

    def _compute_max_levels(self):
        return {
            attr: max(len(levels) for levels in mapping.values()) if mapping else 0
            for attr, mapping in self.hierarchies.items()
        }

    def load_hierarchy(self, attribute, level):
        if attribute not in self.hierarchies:
            raise ValueError(f"Thuộc tính '{attribute}' không tồn tại")
        hierarchy = {}
        for orig, levels in self.hierarchies[attribute].items():
            if level == 0:
                hierarchy[orig] = orig
            elif level - 1 < len(levels):
                hierarchy[orig] = levels[level - 1]
            else:
                hierarchy[orig] = levels[-1]
        return hierarchy