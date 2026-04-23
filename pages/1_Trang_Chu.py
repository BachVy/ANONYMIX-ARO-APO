import streamlit as st

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

# 1. Cấu hình trang
st.set_page_config(page_title="Anonymix - Home", page_icon="🛡️", layout="wide")

# 2. Bộ Icon SVG hiện đại (Cách ly hoàn toàn, không gây lỗi icon hệ thống)
icon_receive = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23004e99' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4' /%3E%3C/svg%3E"
icon_analyze = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23004e99' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' /%3E%3C/svg%3E"
icon_optimize = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23004e99' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M13 10V3L4 14h7v7l9-11h-7z' /%3E%3C/svg%3E"
icon_visual = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23004e99' stroke-width='2'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M15 12a3 3 0 11-6 0 3 3 0 016 0z' /%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' d='M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z' /%3E%3C/svg%3E"

# 3. Hệ thống CSS (Chỉ định danh cho class cụ thể, không dùng !important lên thẻ chung)
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    .stApp { background-color: #f8f9fa; }
    
    /* Font cho tiêu đề */
    h1, h2, h3, h4 { font-family: 'Manrope', sans-serif !important; }
    
    /* Font cho nội dung - Chỉ áp dụng cho văn bản Markdown để không làm lỗi Widget */
    .stMarkdown p, .stMarkdown li, .stMarkdown span { 
        font-family: 'Inter', sans-serif; 
    }

    .signature-gradient-text {
        background: linear-gradient(135deg, #004e99 0%, #0a66c2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        display: inline-block;
    }

    .glass-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        border-left: 5px solid #004e99;
        box-shadow: 0px 10px 40px rgba(25,28,29,0.04);
        height: 100%;
    }

    .benchmark-box {
        background: #004e99;
        color: white;
        padding: 30px;
        border-radius: 20px;
        height: 100%;
    }

    .step-box {
        text-align: center;
        padding: 20px;
        background: white;
        border-radius: 15px;
        border: 1px solid #eee;
        transition: transform 0.3s ease;
        height: 100%;
    }

    .step-box:hover {
        transform: translateY(-5px);
        box-shadow: 0px 5px 15px rgba(0,0,0,0.05);
    }

    .custom-icon-img {
        width: 45px;
        height: 45px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# 4. Header Section
st.markdown("""
    <div style="margin-top: 1rem; margin-bottom: 2rem;">
        <h1 class="signature-gradient-text" style="font-size: 3.2rem; margin-bottom: 0;">🛡️ Anonymix</h1>
        <p style="font-size: 1.3rem; color: #444; font-weight: 600;">
            Hệ thống tối ưu ẩn danh dữ liệu thông minh bằng thuật toán lai ARO-APO
        </p>
    </div>
""", unsafe_allow_html=True)

# 5. PHẦN 1: GIỚI THIỆU TỔNG QUAN
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("""
        <div class="glass-card">
            <h3 style="color: #004e99; margin-top: 0;">🎯 Mục tiêu của hệ thống</h3>
            <p>Trong kỷ nguyên dữ liệu số, việc chia sẻ dữ liệu y tế và cá nhân để nghiên cứu thường gặp rào cản về quyền riêng tư. 
            <b>Anonymix</b> ra đời để giải quyết bài toán cân bằng giữa:</p>
            <ol style="line-height: 1.8;">
                <li><b>Bảo mật (Privacy):</b> Triệt tiêu khả năng tái định danh cá nhân thông qua các mô hình bảo vệ nghiêm ngặt.</li>
                <li><b>Hữu dụng (Utility):</b> Đảm bảo dữ liệu sau ẩn danh vẫn giữ được đặc trưng thống kê để huấn luyện mô hình AI/ML.</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("""
        <div class="benchmark-box">
            <h4 style="color: white; margin-top: 0;">🔍 Thông số Benchmark:</h4>
            <ul style="list-style-type: none; padding-left: 0; line-height: 2;">
                <li>📊 <b>Datasets:</b> 07 bộ dữ liệu chuẩn.</li>
                <li>🏆 <b>Kỷ lục:</b> 50.000 bản ghi Medical.</li>
                <li>🧬 <b>Thuật toán:</b> ARO-APO Hybrid.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

# 6. PHẦN 2: QUY TRÌNH XỬ LÝ (Full Nội Dung & SVG Icon)
st.write("##")
st.markdown("### ⚙️ Quy trình xử lý thông minh")
c1, c2, c3, c4 = st.columns(4)

steps = [
    (icon_receive, "Tiếp nhận", "Hỗ trợ đa dạng dataset (CSV) từ y tế, tài chính."),
    (icon_analyze, "Phân tích k-l-c", "Gợi ý tham số bảo mật dựa trên phân phối thực tế."),
    (icon_optimize, "Tối ưu Hybrid", "Dùng ARO-APO tìm kiếm phân vùng ẩn danh tối ưu."),
    (icon_visual, "Trực quan hóa", "Báo cáo Boxplot và đường cong hội tụ kết quả.")
]

for i, (img_src, title, desc) in enumerate(steps):
    with [c1, c2, c3, c4][i]:
        st.markdown(f"""
            <div class="step-box">
                <img src="{img_src}" class="custom-icon-img">
                <h4 style="margin: 0 0 10px 0; color: #004e99;">{title}</h4>
                <p style="font-size: 0.85rem; color: #666; margin: 0;">{desc}</p>
            </div>
        """, unsafe_allow_html=True)

# 7. PHẦN 3: CÁC MÔ HÌNH BẢO MẬT (Giữ nguyên text đầy đủ)
st.write("##")
with st.expander("📚 Tìm hiểu về các mô hình bảo mật trong Anonymix", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **K-Anonymity:**
        Bản ghi không thể phân biệt được với ít nhất $k-1$ bản ghi khác trong cùng một nhóm định danh (Quasi-identifiers).
        
        **L-Diversity:**
        Ngăn chặn tấn công bằng cách đảm bảo nhóm nhạy cảm có ít nhất $l$ giá trị khác nhau, tránh trường hợp thông tin nhạy cảm quá đơn điệu.
        """)
    with col_b:
        st.markdown("""
        **Recursive (c, l)-Diversity:**
        Đảm bảo giá trị phổ biến nhất không xuất hiện quá thường xuyên so với các giá trị khác trong nhóm, tăng cường khả năng chống lại các cuộc tấn công dựa trên nền tảng kiến thức nền.
        """)

# 8. PHẦN 4: CHÍNH SÁCH & ĐỒNG Ý
st.divider()
st.subheader("⚠️ Cam kết & Miễn trừ trách nhiệm")

with st.container(border=True):
    st.markdown("""
    **Điều khoản sử dụng:**
    * **Mục đích:** Hệ thống dành cho nghiên cứu học thuật và thử nghiệm giải pháp tối ưu hóa ẩn danh.
    * **Dữ liệu:** Chúng tôi không lưu trữ dữ liệu gốc sau phiên làm việc. Người dùng tự chịu trách nhiệm về nội dung tải lên.
    * **Pháp lý:** Việc sử dụng dữ liệu định danh thực tế phải tuân thủ luật bảo vệ dữ liệu cá nhân hiện hành (GDPR, Nghị định 13/2023/NĐ-CP).
    """)
    
    if "legal_agree" not in st.session_state:
        st.session_state.legal_agree = False

    agree = st.checkbox("Tôi xác nhận đã đọc, hiểu và đồng ý tuân thủ các điều khoản trên.", 
                        value=st.session_state.legal_agree, key="main_legal_checkbox")
    st.session_state.legal_agree = agree

    if agree:
        st.success("Cấp quyền thành công! Bạn hiện có thể truy cập các tính năng thực nghiệm.")
        if st.button("Đi tới trang Chạy Thực Nghiệm ngay", type="primary", use_container_width=True):
            st.switch_page("pages/2_Thuc_Nghiem.py")

# Footer
st.markdown("""
    <div style="text-align: center; border-top: 1px solid #eee; margin-top: 50px; padding-top: 20px; color: #888; font-size: 0.9rem;">
        © 2024 Anonymix Project - Khoa học dữ liệu & Bảo mật thông tin.
    </div>
""", unsafe_allow_html=True)