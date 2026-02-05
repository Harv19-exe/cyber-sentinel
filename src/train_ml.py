import numpy as np
import pandas as pd
import joblib
import os
import time
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# CẤU HÌNH
DATA_PATH = "../data/processed"
MODEL_PATH = "../models"
REPORT_PATH = "../reports/figures"

if not os.path.exists(MODEL_PATH):
    os.makedirs(MODEL_PATH)
if not os.path.exists(REPORT_PATH):
    os.makedirs(REPORT_PATH)

def load_data():
    print("⏳ Đang load dữ liệu từ file .npy (Siêu tốc)...")
    X_train = np.load(os.path.join(DATA_PATH, 'X_train.npy'))
    X_test = np.load(os.path.join(DATA_PATH, 'X_test.npy'))
    y_train = np.load(os.path.join(DATA_PATH, 'y_train.npy'))
    y_test = np.load(os.path.join(DATA_PATH, 'y_test.npy'))
    
    # Load Label Encoder để biết số 0 là Benign, 1 là DoS...
    le = joblib.load(os.path.join(DATA_PATH, 'label_encoder.pkl'))
    class_names = [str(cls) for cls in le.classes_]
    
    print(f"✅ Dữ liệu đã sẵn sàng. Train size: {X_train.shape}, Test size: {X_test.shape}")
    return X_train, X_test, y_train, y_test, class_names

def plot_confusion_matrix(y_true, y_pred, classes, model_name):
    """Vẽ ma trận nhầm lẫn để báo cáo"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes)
    plt.title(f'Confusion Matrix - {model_name}')
    plt.ylabel('Thực tế (True Label)')
    plt.xlabel('Dự đoán (Predicted Label)')
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_PATH, f'confusion_matrix_{model_name}.png'))
    print(f"🖼️ Đã lưu ảnh Confusion Matrix tại {REPORT_PATH}")

def train_and_evaluate(model, model_name, X_train, y_train, X_test, y_test, class_names):
    print(f"\n{'='*20} TRAINING {model_name.upper()} {'='*20}")
    start_time = time.time()
    
    # 1. Training
    model.fit(X_train, y_train)
    train_time = time.time() - start_time
    print(f"⏱️ Thời gian train: {train_time:.2f} giây")
    
    # 2. Lưu model
    joblib.dump(model, os.path.join(MODEL_PATH, f'{model_name}.pkl'))
    
    # 3. Dự đoán
    print("🔮 Đang chạy thử nghiệm trên tập Test...")
    y_pred = model.predict(X_test)
    
    # 4. Đánh giá
    acc = accuracy_score(y_test, y_pred)
    print(f"🏆 Accuracy: {acc:.4f}")
    
    print("\n📊 Báo cáo chi tiết (Classification Report):")
    print(classification_report(y_test, y_pred, target_names=class_names, digits=4))
    
    # 5. Vẽ hình
    plot_confusion_matrix(y_test, y_pred, class_names, model_name)

if __name__ == "__main__":
    # 1. Load dữ liệu
    X_train, X_test, y_train, y_test, class_names = load_data()
    
    # ==========================================
    # MODEL 1: DECISION TREE (Cây quyết định)
    # Nhanh, nhẹ, dễ giải thích.
    # ==========================================
    dt_model = DecisionTreeClassifier(random_state=42)
    train_and_evaluate(dt_model, "DecisionTree", X_train, y_train, X_test, y_test, class_names)
    
    # ==========================================
    # MODEL 2: RANDOM FOREST (Rừng ngẫu nhiên)
    # Mạnh mẽ hơn, chống overfitting tốt hơn.
    # n_jobs=-1: Dùng tất cả nhân CPU để chạy song song
    # ==========================================
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    train_and_evaluate(rf_model, "RandomForest", X_train, y_train, X_test, y_test, class_names)
    
    print("\n🚀 [DONE] Đã hoàn thành nhiệm vụ của Role 1 (ML Engineer).")