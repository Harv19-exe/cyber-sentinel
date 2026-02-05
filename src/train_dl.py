import numpy as np
import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils import class_weight # tinh trong so


# CẤU HÌNH
DATA_PATH = "../data/processed"
MODEL_PATH = "../models"
REPORT_PATH = "../reports/figures"

# Thiết lập GPU nếu có (Không bắt buộc)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def load_data():
    print("⏳ Đang load dữ liệu cho Deep Learning...")
    X_train = np.load(os.path.join(DATA_PATH, 'X_train.npy'))
    X_test = np.load(os.path.join(DATA_PATH, 'X_test.npy'))
    y_train = np.load(os.path.join(DATA_PATH, 'y_train.npy'))
    y_test = np.load(os.path.join(DATA_PATH, 'y_test.npy'))
    
    le = joblib.load(os.path.join(DATA_PATH, 'label_encoder.pkl'))
    class_names = [str(cls) for cls in le.classes_]
    
    return X_train, X_test, y_train, y_test, class_names

def build_model(input_dim, num_classes):
    """
    Xây dựng kiến trúc mạng ANN (Artificial Neural Network)
    Cấu trúc hình phễu: To -> Nhỏ dần -> Output
    """
    model = Sequential([
        # Lớp Input & Hidden 1: 128 nơ-ron, hàm kích hoạt ReLU
        Dense(128, input_dim=input_dim, activation='relu'),
        Dropout(0.2), # Tắt ngẫu nhiên 20% nơ-ron để chống học vẹt
        
        # Lớp Hidden 2
        Dense(64, activation='relu'),
        Dropout(0.2),
        
        # Lớp Hidden 3
        Dense(32, activation='relu'),
        
        # Lớp Output: Số nơ-ron = Số lớp (Label), hàm Softmax để ra xác suất
        Dense(num_classes, activation='softmax')
    ])
    
    # Compile mô hình
    # sparse_categorical_crossentropy: Dùng khi nhãn là số nguyên (0, 1, 2...)
    model.compile(optimizer='adam', 
                  loss='sparse_categorical_crossentropy', 
                  metrics=['accuracy'])
    return model

def plot_history(history):
    """Vẽ biểu đồ quá trình học (Loss & Accuracy)"""
    plt.figure(figsize=(12, 5))
    
    # Biểu đồ Accuracy
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Val Accuracy')
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend()
    
    # Biểu đồ Loss
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Val Loss')
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(os.path.join(REPORT_PATH, 'dl_training_history.png'))
    print(f"📈 Đã lưu biểu đồ training tại {REPORT_PATH}")

if __name__ == "__main__":
    # 1. Load Data
    X_train, X_test, y_train, y_test, class_names = load_data()
    
    # 2. Xây dựng Model
    num_classes = len(class_names)
    input_dim = X_train.shape[1]
    
    model = build_model(input_dim, num_classes)
    model.summary() # In ra cấu trúc mạng
    
    # 3. Thiết lập Callback (Tự động lưu và dừng)
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True, verbose=1),
        ModelCheckpoint(os.path.join(MODEL_PATH, 'ann_model.keras'), save_best_only=True)
    ]
    # --- [ĐOẠN CODE MỚI: TÍNH TRỌNG SỐ LỚP] ---
    print("⚖️ Đang tính toán Class Weights để xử lý mất cân bằng...")
    class_weights = class_weight.compute_class_weight(
        class_weight='balanced',
        classes=np.unique(y_train),
        y=y_train
    )
    # Chuyển về dạng dictionary để Keras hiểu: {0: 0.5, 1: 50.0, ...}
    class_weight_dict = dict(enumerate(class_weights))
    print(f"✅ Trọng số đã tính: {class_weight_dict}")
    # ------------------------------------------

    # 4. Training (SỬA LẠI HÀM FIT ĐỂ THÊM class_weight)
    print(f"\n{'='*20} BẮT ĐẦU TRAINING ANN (VỚI CLASS WEIGHTS) {'='*20}")
    history = model.fit(
        X_train, y_train,
        epochs=20,
        batch_size=64,
        validation_split=0.2,
        callbacks=callbacks,
        verbose=1,
        class_weight=class_weight_dict  # <--- QUAN TRỌNG: THÊM THAM SỐ NÀY VÀO
    )
    # 4. Training
    print(f"\n{'='*20} BẮT ĐẦU TRAINING ANN {'='*20}")
    history = model.fit(
        X_train, y_train,
        epochs=20,          # Chạy tối đa 20 vòng
        batch_size=64,      # Mỗi lần học 64 mẫu
        validation_split=0.2, # Dùng 20% tập train để kiểm tra chéo
        callbacks=callbacks,
        verbose=1
    )
    
    # 5. Đánh giá
    print("\n🔮 Đang dự đoán trên tập Test...")
    y_pred_probs = model.predict(X_test)
    y_pred = np.argmax(y_pred_probs, axis=1) # Chọn class có xác suất cao nhất
    
    print("\n📊 Báo cáo chi tiết (Classification Report):")
    print(classification_report(y_test, y_pred, target_names=class_names, digits=4))
    
    # 6. Vẽ biểu đồ học
    plot_history(history)
    
    print("🚀 [DONE] Nhiệm vụ của Role 2 (Deep Learning) hoàn tất.")