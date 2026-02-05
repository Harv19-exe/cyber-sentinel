import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns

# CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Cyber Sentinel AI", page_icon="🛡️", layout="wide")

# LOAD CÁC MODEL VÀ SCALER (CACHE ĐỂ KHÔNG LOAD LẠI MỖI LẦN)
@st.cache_resource
def load_assets():
    base_path = "../data/processed"
    model_path = "../models"
    
    # Load Scaler & Label Encoder
    scaler = joblib.load(os.path.join(base_path, 'scaler.pkl'))
    le = joblib.load(os.path.join(base_path, 'label_encoder.pkl'))
    
    # Load Models
    try:
        rf_model = joblib.load(os.path.join(model_path, 'RandomForest.pkl'))
    except:
        rf_model = None
        
    try:
        dl_model = tf.keras.models.load_model(os.path.join(model_path, 'ann_model.keras'))
    except:
        dl_model = None
        
    return scaler, le, rf_model, dl_model

# GỌI HÀM LOAD
scaler, le, rf_model, dl_model = load_assets()

# --- SIDEBAR (THANH ĐIỀU KHIỂN) ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=100)
st.sidebar.title("⚙️ Cấu hình Hệ thống")
model_choice = st.sidebar.radio("Chọn Model AI:", ["Machine Learning (Random Forest)", "Deep Learning (ANN)"])
confidence_threshold = st.sidebar.slider("Ngưỡng cảnh báo (%)", 0, 100, 50)

# --- MAIN PAGE ---
st.title("🛡️ CYBER SENTINEL - HỆ THỐNG PHÁT HIỆN XÂM NHẬP")
st.markdown("---")

# UPLOAD FILE
uploaded_file = st.file_uploader("Tải lên file log mạng (CSV) để quét:", type=['csv'])

if uploaded_file is not None:
    st.info("🚀 Đang phân tích gói tin...")
    
    # 1. Đọc dữ liệu
    try:
        input_df = pd.read_csv(uploaded_file)
        # Xóa khoảng trắng thừa ở tên cột để khớp với Model
        input_df.columns = input_df.columns.str.strip()
        # Lấy mẫu ngẫu nhiên 50 dòng để demo cho nhanh nếu file quá nặng
        if len(input_df) > 1000:
            st.warning("⚠️ File quá lớn, hệ thống sẽ lấy mẫu 100 dòng đầu tiên để demo.")
            display_df = input_df.head(100).copy()
        else:
            display_df = input_df.copy()
            
        # 2. Tiền xử lý (Giống hệt lúc Train)
        # Lưu ý: Cần chọn đúng các cột Feature mà Model đã học. 
        # Ở đây tôi giả định file upload có đủ cột. Trong thực tế cần bước map column.
        
        # Chỉ lấy các cột số để đưa vào model
        X_input = display_df.select_dtypes(include=[np.number])
        
        # Xử lý số lượng cột (Nếu file upload khác số cột lúc train -> Lỗi)
        # Đây là đoạn giả lập để code chạy được với file raw CIC-IDS:
        # Cắt đúng 78 cột features (bỏ Label)
        if X_input.shape[1] > 78:
            X_input = X_input.iloc[:, :78] 
            
        # Chuẩn hóa
        X_scaled = scaler.transform(X_input)
        
        # 3. Dự đoán
        if model_choice == "Machine Learning (Random Forest)":
            if rf_model:
                y_pred = rf_model.predict(X_scaled)
                # RF không trả về xác suất từng lớp dễ như DL, ta lấy predict thẳng
                pred_labels = le.inverse_transform(y_pred)
            else:
                st.error("❌ Chưa tìm thấy file model Random Forest!")
                st.stop()
                
        else: # Deep Learning
            if dl_model:
                y_probs = dl_model.predict(X_scaled)
                y_pred_idx = np.argmax(y_probs, axis=1)
                pred_labels = le.inverse_transform(y_pred_idx)
            else:
                st.error("❌ Chưa tìm thấy file model Deep Learning!")
                st.stop()
        
        # 4. Hiển thị kết quả
        display_df['AI Prediction'] = pred_labels
        
        # Thống kê
        attack_counts = display_df['AI Prediction'].value_counts()
        total_attacks = len(display_df) - attack_counts.get('BENIGN', 0)
        
        # KPI Cards
        col1, col2, col3 = st.columns(3)
        col1.metric("Tổng gói tin quét", len(display_df))
        col2.metric("Số lượng AN TOÀN", attack_counts.get('BENIGN', 0), delta_color="normal")
        col3.metric("Số lượng CẢNH BÁO", total_attacks, delta_color="inverse")
        
        st.markdown("### 📊 Chi tiết phát hiện")
        
        # Tô màu: Đỏ nếu tấn công, Xanh nếu an toàn
        def highlight_row(row):
            return ['background-color: #ffcccc' if row['AI Prediction'] != 'BENIGN' else '' for _ in row]

        st.dataframe(display_df.style.apply(highlight_row, axis=1))
        
        # Biểu đồ tròn
        if total_attacks > 0:
            st.markdown("### 📉 Phân bố loại tấn công")
            fig, ax = plt.subplots()
            # Bỏ BENIGN ra để xem rõ các loại tấn công
            attack_only = display_df[display_df['AI Prediction'] != 'BENIGN']['AI Prediction'].value_counts()
            ax.pie(attack_only, labels=attack_only.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
            ax.axis('equal')
            st.pyplot(fig)
            
    except Exception as e:
        st.error(f"Lỗi xử lý file: {e}")
        st.info("Mẹo: Hãy chắc chắn file CSV upload lên có cấu trúc giống file CIC-IDS2017.")

else:
    st.write("👈 Mời tải file CSV từ thanh bên trái để bắt đầu.")