# src/data_loader.py
import polars as pl
import os

class DataLoader:
    def __init__(self, data_path):
        self.data_path = data_path

    def load_data(self, sample_size=None):
        """
        Load dữ liệu siêu tốc bằng Polars
        """
        print(f"🚀 [Polars] Đang đọc dữ liệu từ: {self.data_path}...")
        
        try:
            # Polars scan_csv (Lazy Evaluation): Chưa đọc ngay, chỉ quét cấu trúc
            # Giúp tiết kiệm RAM tối đa khi xử lý file GB
            q = pl.scan_csv(self.data_path, ignore_errors=True)
            
            # Chuẩn hóa tên cột (Xóa khoảng trắng) ngay trong query
            # Polars dùng cú pháp functional rất đẹp
            clean_cols = [col.strip() for col in q.columns]
            q = q.select(pl.all().name.map(lambda x: x.strip()))
            
            # Nếu cần lấy mẫu (Sampling)
            if sample_size:
                # Polars collect() mới thực sự load vào RAM
                df = q.collect().sample(n=sample_size, seed=42)
                print(f"⚠️ Đã lấy mẫu ngẫu nhiên {sample_size} dòng để tăng tốc.")
            else:
                df = q.collect()
                
            print(f"✅ Dữ liệu đã lên sàn. Kích thước: {df.shape}")
            
            # Kiểm tra nhanh các loại tấn công có trong file
            if 'Label' in df.columns:
                print("📊 Phân bố nhãn:")
                print(df['Label'].value_counts())
                
            return df
            
        except Exception as e:
            print(f"❌ Lỗi load data: {e}")
            return None

if __name__ == "__main__":
    # Test thử với file CSV cũ của bạn
    # Thay đường dẫn file CSV thật của bạn vào đây để test
    sample_file = "../data/raw/Friday-WorkingHours-Morning.pcap_ISCX.csv"
    if os.path.exists(sample_file):
        loader = DataLoader(sample_file)
        df = loader.load_data(sample_size=10000)
        print(df.head())
    else:
        print("Không tìm thấy file để test.")