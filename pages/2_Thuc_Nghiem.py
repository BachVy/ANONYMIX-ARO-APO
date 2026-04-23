# import streamlit as st
# import config
# from run_batch import run_dataset_experiment
# from pathlib import Path
# import pandas as pd

# def create_custom_sidebar():
#     with st.sidebar:
#         # Thêm Logo hoặc Tiêu đề trang trí
#         st.markdown("<h2 style='text-align: center;'>ANONYMIX</h2>", unsafe_allow_html=True)
#         st.image("screen.png", use_container_width=True) # Nếu bạn có logo
#         st.write("---")
        
#         # Tạo các nút điều hướng
#         # Lưu ý: 'page' phải là đường dẫn chính xác đến file .py trong thư mục dự án
#         st.page_link("pages/1_Trang_Chu.py", label="Trang Chủ", icon="🏠")
#         st.page_link("pages/2_Thuc_Nghiem.py", label="Thực Nghiệm", icon="🧪")
#         st.page_link("pages/3_Bao_Cao.py", label="Báo Cáo Hiệu Năng", icon="📊")
        
#         st.write("---")
#         # Bạn có thể thêm các thông tin phụ bên dưới menu
#         st.caption("Version 1.56.0 | ARO-APO Hybrid")

# # Gọi hàm này ở đầu mỗi trang
# create_custom_sidebar()

# # --- 1. CẤU HÌNH TRANG & TRẠNG THÁI ---
# st.set_page_config(page_title="Anonymix - Execution", page_icon="💠", layout="wide")

# if "run_finished" not in st.session_state:
#     st.session_state.run_finished = False

# if not st.session_state.get("legal_agree", False):
#     st.warning("🔒 Vui lòng xác nhận điều khoản tại Trang Chủ để mở khóa tính năng.")
#     st.stop()

# # --- 2. CSS MODERN (Nâng cấp giao diện sang trọng) ---
# st.markdown("""
# <style>
#     /* Làm đẹp các khối Metric */
#     div[data-testid="stMetric"] {
#         background-color: #ffffff;
#         padding: 15px;
#         border-radius: 12px;
#         border: 1px solid #e2e8f0;
#         box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
#     }
#     /* Label các bước chạy */
#     .step-label {
#         background: linear-gradient(135deg, #004e99, #003366);
#         color: white;
#         padding: 4px 12px;
#         border-radius: 6px;
#         font-size: 11px;
#         font-weight: 700;
#         text-transform: uppercase;
#         letter-spacing: 1px;
#     }
#     /* Tinh chỉnh nút bấm */
#     .stButton>button {
#         border-radius: 8px;
#         transition: all 0.3s ease;
#     }
#     /* Loại bỏ viền thừa của Expander */
#     [data-testid="stExpander"] { border: none !important; }
# </style>
# """, unsafe_allow_html=True)

# st.title("💠 Cấu hình & Thực thi Nghiên cứu")

# # --- 3. LAYOUT CHÍNH ---
# col_left, col_right = st.columns([1.8, 1.2], gap="large")

# with col_left:
#     # --- PHASE 01: DỮ LIỆU ---
#     with st.container(border=True):
#         st.markdown('<span class="step-label">PHASE 01</span>', unsafe_allow_html=True)
#         st.subheader("📑 Nguồn Dữ liệu Hệ thống")
        
#         tab_p, tab_u = st.tabs(["💎 Dataset tiêu chuẩn", "📥 Cổng nạp dữ liệu"])
#         with tab_p:
#             preset = ["medical", "adult", "italia", "cmc", "mgm", "cahousing", "informs"]
#             dataset_to_use = st.selectbox("Chọn bộ dữ liệu:", preset, label_visibility="collapsed")
#             is_upload = False
#         with tab_u:
#             uploaded_file = st.file_uploader("Yêu cầu định dạng CSV", type=["csv"])
#             if uploaded_file:
#                 dataset_to_use = "uploaded"
#                 is_upload = True
#             else: is_upload = False

#     # --- PHASE 02: PHÂN TÍCH ---
#     with st.container(border=True):
#         st.markdown('<span class="step-label">PHASE 02</span>', unsafe_allow_html=True)
#         st.subheader("🛡️ Phân tích Chỉ số Bảo mật")
        
#         try:
#             # Xác định đường dẫn file
#             if is_upload and uploaded_file:
#                 temp_path = config.BASE_DIR / "data" / "uploaded" / uploaded_file.name
#             else:
#                 temp_path = config.BASE_DIR / "data" / dataset_to_use / f"{dataset_to_use}.csv"

#             from run_parallel import analyze_and_suggest_params
#             sen_attr = "PrimaryDiagnosis" if "medical" in dataset_to_use else config.SENSITIVE_ATTRIBUTE
            
#             # Tính toán chỉ số thực
#             k, l, c = analyze_and_suggest_params(str(temp_path), sen_attr)

#             m1, m2, m3 = st.columns(3)
#             m1.metric("k-Anonymity", k, delta="Optimized")
#             m2.metric("l-Diversity", l, delta="Qualified")
#             m3.metric("C-Recursive", f"{c:.2f}", delta="Balanced")
#         except Exception:
#             st.info("💡 Hệ thống đang chờ tín hiệu dữ liệu để tính toán tham số...")

# with col_right:
#     # --- PHASE 03: VẬN HÀNH ---
#     with st.container(border=True):
#         st.markdown('<span class="step-label">PHASE 03</span>', unsafe_allow_html=True)
#         st.subheader("⚙️ Thông số Vận hành")
        
#         trials = st.slider("Số lần chạy:", 1, 30, 10)
#         workers = st.number_input("Tài nguyên xử lý (Workers):", 1, 10, 6)
        
#         st.write("##") 
#         if st.button("⚡ KÍCH HOẠT TIẾN TRÌNH", type="primary", use_container_width=True):
#             # Xử lý lưu file nếu là upload
#             if is_upload:
#                 save_path = config.BASE_DIR / "data" / "uploaded" / uploaded_file.name
#                 save_path.parent.mkdir(exist_ok=True, parents=True)
#                 with open(save_path, "wb") as f: f.write(uploaded_file.getbuffer())
#                 config.INPUT_FILE = save_path
#                 config.DATASET_NAME = "uploaded"
#             else:
#                 config.DATASET_NAME = dataset_to_use
#                 config.INPUT_FILE = config.BASE_DIR / "data" / dataset_to_use / f"{dataset_to_use}.csv"

#             # Thực thi thuật toán
#             with st.status("Đang triển khai thuật toán lai ARO-APO...", expanded=True) as status:
#                 st.write("Đang cấu hình môi trường song song...")
#                 res = run_dataset_experiment(dataset_to_use)
#                 st.write("Đang tổng hợp kết quả...")
#                 status.update(label="Quy trình hoàn tất!", state="complete", expanded=False)
            
#             if res is not None:
#                 st.session_state.run_finished = True # Đánh dấu đã xong
#                 st.balloons()
#                 st.success("Bảo mật dữ liệu thành công!")

#     # --- KHU VỰC ĐIỀU HƯỚNG BÁO CÁO (Lấp đầy khoảng trống) ---
#     if st.session_state.run_finished:
#         with st.container(border=True):
#             st.write("**Kết quả đã sẵn sàng phân tích**")
#             if st.button("TRUY CẬP BÁO CÁO CHI TIẾT 📈", type="secondary", use_container_width=True):
#                 st.switch_page("pages/3_Bao_Cao.py")
#     else:
#         # Hiển thị thông tin bổ trợ khi chưa chạy xong để tránh khoảng trắng
#         st.info(f"**Trạng thái:** Sẵn sàng thực thi trên **{dataset_to_use.upper()}**.")
#         st.image("https://img.freepik.com/free-vector/cyber-security-concept_23-2148532223.jpg", caption="Anonymix Core Framework")




import streamlit as st
import config
from run_batch import run_dataset_experiment
from pathlib import Path
import pandas as pd
import update_results_logic  # Import module xử lý gộp và vẽ biểu đồ
import subprocess
import sys
import os

def create_custom_sidebar():
    with st.sidebar:
        st.markdown("<h2 style='text-align: center;'>ANONYMIX</h2>", unsafe_allow_html=True)
        # Sử dụng try-except để tránh lỗi nếu file screen.png chưa có
        try:
            st.image("screen.png", use_container_width=True)
        except:
            pass
        st.write("---")
        
        st.page_link("pages/1_Trang_Chu.py", label="Trang Chủ", icon="🏠")
        st.page_link("pages/2_Thuc_Nghiem.py", label="Thực Nghiệm", icon="🧪")
        st.page_link("pages/3_Bao_Cao.py", label="Báo Cáo Hiệu Năng", icon="📊")
        
        st.write("---")
        st.caption("Version 1.56.0 | ARO-APO Hybrid")

# --- 1. CẤU HÌNH TRANG & TRẠNG THÁI ---
st.set_page_config(page_title="Anonymix - Execution", page_icon="💠", layout="wide")

# Khởi tạo sidebar
create_custom_sidebar()

if "run_finished" not in st.session_state:
    st.session_state.run_finished = False

if not st.session_state.get("legal_agree", False):
    st.warning("🔒 Vui lòng xác nhận điều khoản tại Trang Chủ để mở khóa tính năng.")
    st.stop()

# --- 2. CSS MODERN ---
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    .step-label {
        background: linear-gradient(135deg, #004e99, #003366);
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button { border-radius: 8px; transition: all 0.3s ease; }
    [data-testid="stExpander"] { border: none !important; }
</style>
""", unsafe_allow_html=True)

st.title("💠 Cấu hình & Thực thi Nghiên cứu")

# --- 3. LAYOUT CHÍNH ---
col_left, col_right = st.columns([1.8, 1.2], gap="large")

with col_left:
    # --- PHASE 01: DỮ LIỆU ---
    with st.container(border=True):
        st.markdown('<span class="step-label">PHASE 01</span>', unsafe_allow_html=True)
        st.subheader("📑 Nguồn Dữ liệu Hệ thống")
        
        tab_p, tab_u = st.tabs(["💎 Dataset tiêu chuẩn", "📥 Cổng nạp dữ liệu"])
        with tab_p:
            preset = ["medical", "adult", "italia", "cmc", "mgm", "cahousing", "informs"]
            dataset_to_use = st.selectbox("Chọn bộ dữ liệu:", preset, label_visibility="collapsed")
            is_upload = False
        with tab_u:
            uploaded_file = st.file_uploader("Yêu cầu định dạng CSV", type=["csv"])
            if uploaded_file:
                dataset_to_use = "uploaded"
                is_upload = True
            else: is_upload = False

    # --- PHASE 02: PHÂN TÍCH ---
    with st.container(border=True):
        st.markdown('<span class="step-label">PHASE 02</span>', unsafe_allow_html=True)
        st.subheader("🛡️ Phân tích Chỉ số Bảo mật")
        
        try:
            if is_upload and uploaded_file:
                temp_path = config.BASE_DIR / "data" / "uploaded" / uploaded_file.name
            else:
                temp_path = config.BASE_DIR / "data" / dataset_to_use / f"{dataset_to_use}.csv"

            from run_parallel import analyze_and_suggest_params
            sen_attr = "PrimaryDiagnosis" if "medical" in dataset_to_use else config.SENSITIVE_ATTRIBUTE
            
            k, l, c = analyze_and_suggest_params(str(temp_path), sen_attr)

            m1, m2, m3 = st.columns(3)
            m1.metric("k-Anonymity", k, delta="Optimized")
            m2.metric("l-Diversity", l, delta="Qualified")
            m3.metric("C-Recursive", f"{c:.2f}", delta="Balanced")
        except Exception:
            st.info("💡 Hệ thống đang chờ tín hiệu dữ liệu để tính toán tham số...")

with col_right:
    # --- PHASE 03: VẬN HÀNH ---
    with st.container(border=True):
        st.markdown('<span class="step-label">PHASE 03</span>', unsafe_allow_html=True)
        st.subheader("⚙️ Thông số Vận hành")
        
        trials = st.slider("Số lần chạy:", 1, 30, 10)
        workers = st.number_input("Tài nguyên xử lý (Workers):", 1, 10, 6)
        
        st.write("##") 
        if st.button("⚡ KÍCH HOẠT TIẾN TRÌNH", type="primary"):
            with st.status("Hệ thống đang thực thi bên ngoài (Safety Mode)...", expanded=True) as status:
                st.write(f"Đang tạo tiến trình độc lập cho {dataset_to_use}...")

                # 1. Cấu hình môi trường an toàn
                my_env = os.environ.copy()
                my_env["PYTHONIOENCODING"] = "utf-8"
                
                # 2. Định nghĩa lệnh chạy
                cmd = [sys.executable, "bridge_runner.py", dataset_to_use]
                
                # 3. Khởi chạy tiến trình (Chỉ gọi MỘT lần duy nhất)
                process = subprocess.Popen(
                    cmd, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    encoding='utf-8', 
                    errors='replace', # Thay thế ký tự lỗi bằng dấu ? thay vì văng lỗi
                    env=my_env,
                    bufsize=1, # Line buffering để log hiện ra ngay lập tức
                    universal_newlines=True
                )
                
                # 4. Đọc log thời gian thực
                # Sử dụng iter để đọc từng dòng từ stdout
                for line in iter(process.stdout.readline, ""):
                    st.write(f"⚙️ {line.strip()}")
                    
                # 5. Đợi kết quả cuối cùng và xử lý lỗi
                return_code = process.wait()
                stderr_output = process.stderr.read()
                
                if return_code == 0:
                    status.update(label="Thực thi thành công!", state="complete")
                    st.session_state.run_finished = True
                    st.balloons()
                    st.success("Dữ liệu đã được xử lý và lưu vào thư mục results.")
                else:
                    status.update(label="Thực thi thất bại!", state="error")
                    st.error(f"Lỗi thực thi bên ngoài (Code {return_code}):")
                    st.code(stderr_output) # Hiển thị lỗi chi tiết trong khối code cho dễ nhìn

    # --- KHU VỰC ĐIỀU HƯỚNG BÁO CÁO ---
    if st.session_state.run_finished:
        with st.container(border=True):
            st.write("**Kết quả đã sẵn sàng phân tích**")
            if st.button("TRUY CẬP BÁO CÁO CHI TIẾT 📈", type="secondary", use_container_width=True):
                st.switch_page("pages/3_Bao_Cao.py")
    else:
        st.info(f"**Trạng thái:** Sẵn sàng thực thi trên **{dataset_to_use.upper()}**.")
        st.image("https://img.freepik.com/free-vector/cyber-security-concept_23-2148532223.jpg", caption="Anonymix Core Framework")