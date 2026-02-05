import pandas as pd
import numpy as np
import os
import glob
import sys

class CICIDSLoader:
    """
    Class chuyên dụng để load và xử lý thô bộ dữ liệu CIC-IDS2017.
    Tự động xử lý lỗi tên cột, loại bỏ giá trị vô cực và tối ưu bộ nhớ.
    """
    
    def __init__(self, raw_data_path, processed_data_path):
        self.raw_path = raw_data_path
        self.processed_path = processed_data_path
        
        # Đảm bảo thư mục tồn tại
        if not os.path.exists(self.processed_path):
            os.makedirs(self.processed_path)

    def clean_column_names(self, df):
        """
        Xử lý vấn đề lớn nhất của CIC-IDS2017: Tên cột chứa khoảng trắng thừa.
        Ví dụ: ' Flow Duration ' -> 'Flow Duration'
        """
        df.columns = df.columns.str.strip()
        print("✅ [INFO] Đã chuẩn hóa tên các cột (Removed whitespaces).")
        return df

    def optimize_dtypes(self, df):
        """
        Giảm dung lượng RAM bằng cách chuyển float64 -> float32
        """
        ints = df.select_dtypes(include=['int64', 'int32']).columns
        floats = df.select_dtypes(include=['float64']).columns
        
        df[ints] = df[ints].apply(pd.to_numeric, downcast='integer')
        df[floats] = df[floats].apply(pd.to_numeric, downcast='float')
        
        print(f"✅ [INFO] Đã tối ưu hóa kiểu dữ liệu. RAM hiện tại: {df.memory_usage().sum() / 1024**2:.2f} MB")
        return df

    def handle_infinity_and_null(self, df):
        """
        Thay thế Infinity bằng NaN, sau đó xóa hoặc điền giá trị.
        Các model Sklearn/Tensorflow sẽ crash nếu gặp Infinity.
        """
        # Thay thế inf và -inf bằng NaN
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        # Kiểm tra số lượng NaN
        null_count = df.isna().sum().sum()
        if null_count > 0:
            print(f"⚠️ [WARNING] Phát hiện {null_count} giá trị NaN/Infinity. Đang tiến hành loại bỏ...")
            df.dropna(inplace=True) # Với dữ liệu lớn, drop là an toàn nhất cho giai đoạn đầu
            
        print("✅ [INFO] Đã xử lý sạch Infinity và Null.")
        return df

    def load_and_merge(self, sample_ratio=1.0):
        """
        Load tất cả file CSV trong thư mục raw, gộp lại thành 1 file duy nhất.
        sample_ratio: Tỉ lệ lấy mẫu (ví dụ 0.1 để lấy 10% dữ liệu test code).
        """
        all_files = glob.glob(os.path.join(self.raw_path, "*.csv"))
        
        if not all_files:
            print(f"❌ [ERROR] Không tìm thấy file .csv nào trong {self.raw_path}")
            sys.exit(1)
            
        print(f"🚀 [START] Tìm thấy {len(all_files)} files. Đang bắt đầu xử lý...")
        
        df_list = []
        
        for filename in all_files:
            print(f"   -> Đang đọc: {os.path.basename(filename)}...")
            try:
                # Đọc file, encoding latin1 thường an toàn hơn utf-8 cho CIC-IDS
                df_temp = pd.read_csv(filename, encoding='cp1252', low_memory=False)
                
                # Làm sạch tên cột ngay lập tức để tránh lỗi khi merge
                df_temp = self.clean_column_names(df_temp)
                
                # Lấy mẫu nếu cần (để tránh tràn RAM khi dev)
                if sample_ratio < 1.0:
                    df_temp = df_temp.sample(frac=sample_ratio, random_state=42)
                
                df_list.append(df_temp)
            except Exception as e:
                print(f"❌ [ERROR] Lỗi khi đọc file {filename}: {e}")

        # Gộp tất cả thành 1 DataFrame lớn
        print("🔄 [PROCESSING] Đang gộp dữ liệu (Merging)...")
        full_df = pd.concat(df_list, axis=0, ignore_index=True)
        
        # Xử lý làm sạch sâu
        full_df = self.handle_infinity_and_null(full_df)
        full_df = self.optimize_dtypes(full_df)
        
        # Lưu file đã xử lý
        output_file = os.path.join(self.processed_path, 'cic_ids_2017_merged.csv')
        print(f"💾 [SAVING] Đang lưu file gộp tại: {output_file}")
        full_df.to_csv(output_file, index=False)
        print("✅ [DONE] Hoàn tất quá trình Load Data.")
        
        return full_df

# Phần này để test nhanh khi chạy trực tiếp file này
if __name__ == "__main__":
    # Cấu hình đường dẫn (Sửa lại cho đúng với máy của bạn)
    RAW_PATH = "../data/raw" 
    PROCESSED_PATH = "../data/processed"
    
    loader = CICIDSLoader(RAW_PATH, PROCESSED_PATH)
    
    # LƯU Ý: Lần đầu chạy thử nên để sample_ratio=0.1 (10%) để test code trước
    loader.load_and_merge(sample_ratio=0.1)