# import streamlit as st
# import pandas as pd
# from pathlib import Path

# st.title("📊 Phân tích & Đánh giá Kết quả")

# # Hàm tự động quét và hiển thị biểu đồ
# def display_auto_charts(pattern, title):
#     st.markdown(f"#### {title}")
#     charts = list(Path("results/").glob(f"{pattern}*.png"))
#     if charts:
#         cols = st.columns(len(charts)) if len(charts) <= 2 else st.columns(2)
#         for i, chart_path in enumerate(charts):
#             with cols[i % len(cols)]:
#                 st.image(str(chart_path), caption=f"Phân tích: {chart_path.stem}", use_container_width=True)
#     else:
#         st.info(f"Chưa có biểu đồ {title.lower()}.")

# # Nội dung các Tabs
# tab1, tab2, tab3 = st.tabs(["📈 Tổng quan", "🎯 Hội tụ", "🔍 Chi tiết Dataset"])

# with tab1:
#     display_auto_charts("ALL_IN_ONE", "So sánh Tổng thể thuật toán")

# with tab2:
#     display_auto_charts("ALL_IN_ONE_Convergence", "Đường cong hội tụ ARO-APO")

# with tab3:
#     st.subheader("Biểu đồ chi tiết từng bộ dữ liệu")
#     # Thay vì thông báo "Đã tạo", ta hiển thị luôn các file Boxplot_*.png
#     display_auto_charts("Boxplot", "Phân tích Boxplot")

# # Thêm bảng thống kê cuối trang để "End user" đọc số liệu thực
# with st.expander("📋 Xem bảng số liệu chi tiết (Master Data)"):
#     master_file = Path("results/MASTER_RAW_ALL_DATASETS.csv")
#     if master_file.exists():
#         df_master = pd.read_csv(master_file)
#         st.dataframe(df_master, use_container_width=True)
#         st.download_button("📥 Tải báo cáo CSV", df_master.to_csv(), "report.csv")





import streamlit as st
import pandas as pd
from pathlib import Path

def create_custom_sidebar():
    with st.sidebar:
        # Thêm Logo hoặc Tiêu đề trang trí
        st.markdown("<h2 style='text-align: center;'>ANONYMIX</h2>", unsafe_allow_html=True)
        st.image("screen.png", use_container_width=True) # Nếu bạn có logo
        st.write("---")
        
        # Tạo các nút điều hướng
        # Lưu ý: 'page' phải là đường dẫn chính xác đến file .py trong thư mục dự án
        st.page_link("pages/1_Trang_Chu.py", label="Trang Chủ", icon="🏠")
        st.page_link("pages/2_Thuc_Nghiem.py", label="Thực Nghiệm", icon="🧪")
        st.page_link("pages/3_Bao_Cao.py", label="Báo Cáo Hiệu Năng", icon="📊")
        
        st.write("---")
        # Bạn có thể thêm các thông tin phụ bên dưới menu
        st.caption("Version 1.56.0 | ARO-APO Hybrid")

# Gọi hàm này ở đầu mỗi trang
create_custom_sidebar()

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(page_title="Anonymix - Performance Report", page_icon="📊", layout="wide")

# --- 2. CSS CUSTOM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700;800&family=Inter:wght@400;600&display=swap');
    .main { background-color: #f8f9fa; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif !important; color: #191c1d; }
    .stats-card {
        background-color: white;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e7e8e9;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    .stats-label { color: #414752; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
    .stats-value { font-size: 32px; font-weight: 800; color: #004e99; }
    .insight-box {
        background: linear-gradient(135deg, #004e99, #0a66c2);
        color: white;
        padding: 20px;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. LOGIC XỬ LÝ DỮ LIỆU ---
results_path = Path("results/")
master_file = results_path / "MASTER_RAW_ALL_DATASETS.csv"

@st.cache_data
def get_master_data(file_path):
    if file_path.exists():
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip() # Làm sạch tên cột
        return df
    return None

df = get_master_data(master_file)

# --- 4. HEADER ---
col_h1, col_h2 = st.columns([2, 1])
with col_h1:
    st.title("📊 Performance Analytics")
    st.markdown("<p style='color: #414752; margin-top:-15px;'>Anonymization benchmark: ARO-APO Optimization</p>", unsafe_allow_html=True)
with col_h2:
    st.write("##")
    if df is not None:
        st.download_button("📥 Export Full Report", df.to_csv(index=False), "Anonymix_Full_Report.csv", use_container_width=True)

# --- 5. STATS ROW (Logic Minimization) ---
if df is not None:
    total_records = len(df)
    
    if 'Best_Fitness' in df.columns:
        df['Best_Fitness'] = pd.to_numeric(df['Best_Fitness'], errors='coerce')
        avg_fitness = df['Best_Fitness'].mean()
        min_fitness = df['Best_Fitness'].min()
        
        # --- LOGIC ƯU TIÊN ARO-APO ---
        # 1. Tìm tất cả các dòng có fitness bằng với giá trị nhỏ nhất
        best_rows = df[df['Best_Fitness'] == min_fitness]
        
        if not best_rows.empty:
            # 2. Kiểm tra xem trong các dòng tốt nhất đó có ARO-APO không
            aro_apo_best = best_rows[best_rows['Algorithm'].str.contains('ARO-APO', case=False, na=False)]
            
            if not aro_apo_best.empty:
                best_algo = "ARO-APO" # Ưu tiên lấy ARO-APO
            else:
                best_algo = best_rows.iloc[0]['Algorithm'] # Nếu ko có ARO-APO thì lấy thuật toán đầu tiên
        else:
            best_algo = "N/A"
    else:
        avg_fitness = 0.0
        best_algo = "N/A"
        min_fitness = 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stats-card"><div class="stats-label">Total Experiments</div><div class="stats-value">{total_records}</div><div style="color: #059669; font-size: 12px; font-weight: bold;">↑ Live tracking</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stats-card"><div class="stats-label">Avg. Fitness (Loss)</div><div class="stats-value">{avg_fitness:.4f}</div><div style="color: #004e99; font-size: 12px; font-weight: bold;">Lower is better</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stats-card"><div class="stats-label">Best Min. Fitness</div><div class="stats-value" style="font-size: 24px; padding-top:10px;">{best_algo} ({min_fitness:.4f})</div></div>', unsafe_allow_html=True)

st.write("---")

# --- 6. TABBED ANALYSIS SECTION ---
tab_overview, tab_convergence, tab_details = st.tabs(["📈 Comparison Overview", "🎯 Convergence Analysis", "🔍 Dataset Details"])

# with tab_overview:
#     col_chart, col_insight = st.columns([2, 1])
#     with col_chart:
#         st.subheader("Acuracy Comparison")
#         all_in_one = list(results_path.glob("ALL_IN_ONE_*.png"))
#         if all_in_one:
#             cols = st.columns(4)
#             for i, path in enumerate(all_in_one):
#                 with cols[i % 4]:
#                     st.image(str(path), use_container_width=True)
with tab_overview:
    col_chart, col_insight = st.columns([2.5, 1]) # Tăng nhẹ tỷ trọng cho cột chart
    with col_chart:
        st.subheader("Accuracy & Convergence Comparison")
        all_in_one = list(results_path.glob("ALL_IN_ONE_*.png"))
        
        if all_in_one:
            # Sắp xếp để hình Convergence hoặc Accuracy quan trọng hiện lên trước
            for path in sorted(all_in_one): 
                st.image(str(path), use_container_width=True)
                st.divider() # Thêm đường kẻ giữa các hình cho thoáng
        # if all_in_one:
        #     st.image(str(all_in_one[0]), use_container_width=True)
        else:
            st.info("Chưa có biểu đồ so sánh tổng thể.")
            
    with col_insight:
        st.markdown("""
        <div class="insight-box">
            <p style="font-size: 10px; font-weight: 700; opacity: 0.8; text-transform: uppercase;">Optimization Insight</p>
            <h3 style="color: white; margin-bottom: 15px;">Target: Global Minimum</h3>
            <p style="font-size: 13px; line-height: 1.6;">
                Hệ thống đang tìm kiếm giá trị <b>Fitness nhỏ nhất</b> để tối ưu hóa sự cân bằng giữa tính riêng tư và hữu dụng của dữ liệu.
            </p>
        </div>
        """, unsafe_allow_html=True)

with tab_convergence:
    st.subheader("Optimization Convergence (ARO-APO)")
    conv_charts = list(results_path.glob("ALL_IN_ONE_Convergence*.png"))
    if conv_charts:
        st.image(str(conv_charts[0]), use_container_width=True)

with tab_details:
    st.subheader("Per-Dataset Boxplot Analysis")
    boxplots = sorted(list(results_path.glob("Boxplot_*.png")))
    if boxplots:
        cols = st.columns(2)
        for i, path in enumerate(boxplots):
            with cols[i % 2]:
                st.image(str(path), use_container_width=True)

# --- 7. DATA LOG TABLE (Updated Gradient) ---
st.write("---")
st.subheader("📋 Experiment Data Log")

if df is not None:
    if 'Best_Fitness' in df.columns:
        # Đảo ngược bảng màu: 'Blues_r' (r = reverse) 
        # để giá trị NHỎ NHẤT (tốt nhất) được tô đậm nhất
        st.dataframe(
            df.style.format({'Best_Fitness': '{:.4f}'}, na_rep="N/A"),
            use_container_width=True,
            height=400
        )
    else:
        st.warning("⚠️ Không tìm thấy cột 'Best_Fitness'.")
        st.dataframe(df, use_container_width=True)
else:
    st.error("Không tìm thấy tệp MASTER_RAW_ALL_DATASETS.csv.")

st.markdown("<br><p style='text-align: center; color: #727783; font-size: 12px;'>© 2024 Anonymix Data Security Platform</p>", unsafe_allow_html=True)