import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import joblib # Để lưu scaler dùng lại cho web app
import os

class DataPreprocessor:
    def __init__(self, data_path, output_path):
        self.data_path = data_path
        self.output_path = output_path
        # Đảm bảo thư mục output tồn tại
        if not os.path.exists(output_path):
            os.makedirs(output_path)

    def load_data(self):
        print(f"⏳ Đang đọc dữ liệu từ {self.data_path}...")
        df = pd.read_csv(self.data_path)
        # Xóa khoảng trắng ở tên cột lần nữa cho chắc
        df.columns = df.columns.str.strip()
        return df

    def group_labels(self, df):
        """
        Chiến lược gom nhóm nhãn để giảm mất cân bằng.
        """
        print("🔄 Đang gom nhóm các loại tấn công (Label Grouping)...")
        
        # Tạo từ điển ánh xạ
        attack_group = {
            # DoS Group
            'DoS Hulk': 'DoS',
            'DoS GoldenEye': 'DoS',
            'DoS slowloris': 'DoS',
            'DoS Slowhttptest': 'DoS',
            
            # Web Attack Group
            'Web Attack _ Brute Force': 'Web Attack',
            'Web Attack _ XSS': 'Web Attack',
            'Web Attack _ Sql Injection': 'Web Attack',
            # Lưu ý: Tên cột trong CSV có thể bị lỗi font, cần check kỹ hoặc dùng str.contains
            
            # Brute Force Group
            'FTP-Patator': 'Brute Force',
            'SSH-Patator': 'Brute Force'
        }
        
        # Áp dụng thay thế
        df['Label'] = df['Label'].replace(attack_group)
        
        # Sửa lỗi tên Web Attack bị lỗi font đặc biệt (nếu replace trên không bắt được)
        df.loc[df['Label'].str.contains('Web Attack', case=False, na=False), 'Label'] = 'Web Attack'

        # Loại bỏ các class quá nhỏ (Heartbleed, Infiltration)
        drop_labels = ['Heartbleed', 'Infiltration']
        df = df[~df['Label'].isin(drop_labels)]
        
        print(f"✅ Phân bố nhãn sau khi gom nhóm:\n{df['Label'].value_counts()}")
        return df

    def process_and_save(self):
        df = self.load_data()
        df = self.group_labels(df)
        
        # 1. Tách Feature và Label
        X = df.drop('Label', axis=1)
        y = df['Label']
        
        # 2. Mã hóa Label (Text -> Số)
        print("🔢 Đang mã hóa nhãn (Label Encoding)...")
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        
        # Lưu lại LabelEncoder để sau này Web App biết 0 là gì, 1 là gì
        joblib.dump(le, os.path.join(self.output_path, 'label_encoder.pkl'))
        
        # 3. Chuẩn hóa dữ liệu (Scaling) - CỰC QUAN TRỌNG CHO DEEP LEARNING
        # Đưa toàn bộ số về khoảng [0, 1]
        print("⚖️ Đang chuẩn hóa dữ liệu (MinMax Scaling)...")
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Lưu Scaler
        joblib.dump(scaler, os.path.join(self.output_path, 'scaler.pkl'))
        
        # 4. Chia tập Train / Test (80% Train - 20% Test)
        # stratify=y để đảm bảo tỉ lệ tấn công ở 2 tập là như nhau
        print("✂️ Đang chia tập Train/Test...")
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # 5. Lưu kết quả ra file numpy (.npy) cho nhanh (CSV load rất chậm)
        print("💾 Đang lưu file đã xử lý (.npy)...")
        np.save(os.path.join(self.output_path, 'X_train.npy'), X_train)
        np.save(os.path.join(self.output_path, 'X_test.npy'), X_test)
        np.save(os.path.join(self.output_path, 'y_train.npy'), y_train)
        np.save(os.path.join(self.output_path, 'y_test.npy'), y_test)
        
        print("🚀 [DONE] Hoàn tất Tiền xử lý. Sẵn sàng train!")

if __name__ == "__main__":
    # Đường dẫn file gộp bạn đã tạo ở bước trước
    INPUT_DATA = "../data/processed/cic_ids_2017_merged.csv"
    OUTPUT_DIR = "../data/processed"
    
    preprocessor = DataPreprocessor(INPUT_DATA, OUTPUT_DIR)
    preprocessor.process_and_save()