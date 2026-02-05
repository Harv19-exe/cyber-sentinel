import polars as pl
import numpy as np
import xgboost as xgb
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import LabelEncoder

# CẤU HÌNH
DATA_PATH = "../data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv" # Hoặc file gộp nếu bạn có
MODEL_DIR = "../models"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_xgboost():
    print("🚀 [Polars] Đang load dữ liệu thô...")
    
    # 1. Load data bằng Polars (Siêu nhanh)
    # Lazy loading: Chưa đọc hết vào RAM, chỉ quét cấu trúc
    q = pl.scan_csv(DATA_PATH, ignore_errors=True)
    
    # Chuẩn hóa tên cột (xóa khoảng trắng)
    q = q.select(pl.all().name.map(lambda x: x.strip()))
    
    # Gom nhóm nhãn (Label Grouping) - Giống quy trình chuẩn
    # Polars dùng cú pháp when/then/otherwise cực nhanh
    q = q.with_columns(
        pl.col("Label").str.replace("Web Attack.*", "Web Attack")
        .str.replace("DoS.*", "DoS")
        .str.replace("FTP-Patator", "Brute Force")
        .str.replace("SSH-Patator", "Brute Force")
    )
    
    # Lọc bỏ nhãn rác (Heartbleed, Infiltration) nếu có
    # Ở đây file Friday chỉ có Bot/Benign nên ta cứ giữ nguyên logic chung
    
    # Collect về DataFrame thật (Lấy 100% dữ liệu hoặc sample nếu máy yếu)
    print("⏳ Đang nạp dữ liệu vào RAM...")
    df = q.collect()
    
    # 2. Tiền xử lý (Preprocessing)
    print(f"📊 Kích thước dữ liệu: {df.shape}")
    print(f"🏷️ Phân bố nhãn:\n{df['Label'].value_counts()}")

    # Tách Feature (X) và Label (y)
    # Lấy tất cả cột trừ Label. XGBoost cần số, nên Polars sẽ tự xử lý hoặc ta ép kiểu
    y_raw = df["Label"].to_list()
    
    # Loại bỏ các cột không phải số (như Flow ID, IP, Time...) nếu file có
    # Ở file CIC-IDS gốc, ta chỉ giữ lại 78 cột chỉ số kỹ thuật
    # Cách nhanh nhất: Chỉ lấy các cột kiểu số (Float/Int)
    X_df = df.select(pl.col(pl.Float64, pl.Int64))
    
    # Chuyển sang Numpy để đưa vào XGBoost
    X = X_df.to_numpy()
    print("🧹 Đang xử lý các giá trị Vô cực (Infinity)...")
    # Biến số Vô cực thành 0 để Model không bị lỗi
    X[np.isinf(X)] = 0
    # Biến số Not-a-Number (NaN) thành 0 luôn cho chắc
    X[np.isnan(X)] = 0
    # Mã hóa nhãn (String -> Số: 0, 1, 2...)
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    
    # Lưu Label Encoder để sau này Web App dùng giải mã
    joblib.dump(le, os.path.join(MODEL_DIR, "xgboost_label_encoder.pkl"))
    print(f"✅ Đã mã hóa {len(le.classes_)} loại tấn công: {le.classes_}")

    # 3. Chia tập Train/Test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 4. Training XGBoost (The Beast)
    print("\n🔥 BẮT ĐẦU HUẤN LUYỆN XGBOOST...")
    model = xgb.XGBClassifier(
        objective='multi:softmax',  # Phân loại đa lớp
        num_class=len(le.classes_), # Số lượng lớp
        n_estimators=100,           # Số lượng cây (Trees)
        learning_rate=0.1,          # Tốc độ học
        max_depth=6,                # Độ sâu của cây (càng sâu càng giỏi nhưng dễ học vẹt)
        n_jobs=-1,                  # Dùng full nhân CPU
        tree_method="hist",         # Tối ưu tốc độ training
        eval_metric='mlogloss'
    )
    
    model.fit(X_train, y_train)
    print("🎉 Training hoàn tất!")

    # 5. Đánh giá
    print("\n🔮 Đang dự đoán trên tập Test...")
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    print(f"🏆 Accuracy: {acc:.4f}")
    print("\n📊 Báo cáo chi tiết (Classification Report):")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # 6. Lưu Model
    model_path = os.path.join(MODEL_DIR, "xgboost_model.json")
    model.save_model(model_path)
    print(f"💾 Đã lưu model tại: {model_path}")

if __name__ == "__main__":
    train_xgboost()