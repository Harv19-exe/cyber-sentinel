import streamlit as st
import polars as pl
import numpy as np
import xgboost as xgb
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


pd.set_option("styler.render.max_elements", 1_000_000)
# CẤU HÌNH TRANG
st.set_page_config(page_title="Cyber Sentinel v2.0", page_icon="🛡️", layout="wide")

# --- HÀM LOAD MODEL & ASSETS ---
@st.cache_resource
def load_assets():
    # Lấy đường dẫn tuyệt đối của file app.py hiện tại
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Trỏ ngược ra thư mục cha (CYBER-SENTINEL), rồi vào models
    model_path = os.path.join(current_dir, "..", "models")
    
    print(f"🔍 Đang tìm model tại: {model_path}")
    
    # 1. Load XGBoost (Vua tốc độ)
    xgb_model = xgb.XGBClassifier()
    try:
        json_path = os.path.join(model_path, "xgboost_model.json")
        pkl_path = os.path.join(model_path, "xgboost_label_encoder.pkl")
        
        # Kiểm tra file có tồn tại không trước khi load
        if not os.path.exists(json_path):
            print(f"❌ Không thấy file JSON tại: {json_path}")
            return None, None
            
        xgb_model.load_model(json_path)
        le_xgb = joblib.load(pkl_path)
        print("✅ Load XGBoost thành công!")
    except Exception as e:
        print(f"❌ Lỗi load model: {e}")
        xgb_model = None
        le_xgb = None
        
    return xgb_model, le_xgb

xgb_model, le_xgb = load_assets()

# --- GIAO DIỆN ---
st.title("🛡️ CYBER SENTINEL 2.0 - ENTERPRISE EDITION")
st.markdown("### Hệ thống phát hiện xâm nhập thế hệ mới với Polars & XGBoost")
st.markdown("---")

# Sidebar
st.sidebar.title("⚙️ Cấu hình")
model_choice = st.sidebar.radio(
    "Chọn Engine AI:", 
    ["XGBoost (Recommended - 99% Acc)", "Deep Learning (Legacy)", "Random Forest (Legacy)"]
)

# Upload File
uploaded_file = st.file_uploader("Tải lên log mạng (CSV):", type=['csv'])

if uploaded_file is not None:
    st.info("🚀 Đang xử lý dữ liệu siêu tốc bằng Polars...")
    
    try:
        # 1. ĐỌC FILE BẰNG POLARS (Siêu nhanh)
        # Polars đọc trực tiếp từ buffer upload
        df = pl.read_csv(uploaded_file, ignore_errors=True)
        
        # Chuẩn hóa tên cột (Xóa khoảng trắng)
        old_cols = df.columns
        new_cols = [c.strip() for c in old_cols]
        df = df.rename(dict(zip(old_cols, new_cols)))
        
        # Lấy mẫu nếu file quá lớn (> 5000 dòng)
        if df.height > 5000:
            st.warning(f"⚠️ File chứa {df.height} gói tin. Hệ thống sẽ lấy mẫu ngẫu nhiên 5000 gói để phân tích nhanh.")
            df = df.sample(n=5000, seed=42)
            
        # 2. TIỀN XỬ LÝ CHO XGBOOST
        if "XGBoost" in model_choice:
            if xgb_model is None:
                st.error("❌ Không tìm thấy model XGBoost! Hãy chạy train_xgboost.py trước.")
                st.stop()
                
            # Chỉ lấy cột số (Float/Int)
            X_df = df.select(pl.col(pl.Float64, pl.Int64))
            
            # Chuyển sang Numpy & Xử lý Vô cực (Inf)
            X = X_df.to_numpy()
            X[np.isinf(X)] = 0
            X[np.isnan(X)] = 0
            
            # 3. DỰ ĐOÁN
            y_pred_idx = xgb_model.predict(X)
            
            # Giải mã nhãn (0 -> BENIGN, 1 -> Bot...)
            pred_labels = le_xgb.inverse_transform(y_pred_idx.astype(int))
            
            # Gán kết quả vào DataFrame để hiển thị
            # Polars thao tác cột cực nhanh
            df_display = df.with_columns(pl.Series(name="AI Prediction", values=pred_labels))
            
            # Chuyển về Pandas chỉ để hiển thị trên Streamlit (Streamlit chưa hỗ trợ Polars native tốt lắm)
            display_pandas = df_display.to_pandas()
            
            # 4. THỐNG KÊ & HIỂN THỊ
            st.success("✅ Phân tích hoàn tất!")
            
            # Đẩy các dòng Tấn công lên đầu
            display_pandas['is_attack'] = display_pandas['AI Prediction'].apply(lambda x: 0 if x == 'BENIGN' else 1)
            display_pandas = display_pandas.sort_values(by='is_attack', ascending=False).drop(columns=['is_attack'])
            
            # KPI Cards
            attack_counts = display_pandas['AI Prediction'].value_counts()
            total_attacks = len(display_pandas) - attack_counts.get('BENIGN', 0)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Tổng gói tin", len(display_pandas))
            c2.metric("An toàn (BENIGN)", attack_counts.get('BENIGN', 0))
            c3.metric("CẢNH BÁO TẤN CÔNG", total_attacks, delta_color="inverse")
            
            # Bảng màu
            def highlight_row(row):
                return ['background-color: #ffcccc' if row['AI Prediction'] != 'BENIGN' else '' for _ in row]
                
            st.dataframe(display_pandas.style.apply(highlight_row, axis=1))
            
            # Biểu đồ
            if total_attacks > 0:
                st.markdown("### 📉 Phân loại tấn công")
                # Lọc bỏ BENIGN để biểu đồ tập trung vào tấn công
                attack_only = display_pandas[display_pandas['AI Prediction'] != 'BENIGN']
                
                if not attack_only.empty:
                    fig, ax = plt.subplots(figsize=(8, 4))
                    sns.countplot(data=attack_only, y='AI Prediction', palette='viridis', order=attack_only['AI Prediction'].value_counts().index)
                    plt.title("Thống kê các loại tấn công phát hiện được")
                    st.pyplot(fig)

        else:
            st.info("⚠️ Chế độ Legacy (RandomForest/ANN) đang được bảo trì để nâng cấp lên Polars. Vui lòng chọn XGBoost.")

    except Exception as e:
        st.error(f"Lỗi xử lý: {e}")

else:
    st.write("👈 Mời tải file log mạng từ thanh bên trái.")