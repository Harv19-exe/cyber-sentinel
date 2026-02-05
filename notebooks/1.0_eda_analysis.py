import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# CẤU HÌNH ĐƯỜNG DẪN
# Nếu bạn đã chạy data_loader.py thành công, file gộp sẽ nằm ở đây:
INPUT_FILE = "../data/processed/cic_ids_2017_merged.csv"

# Nếu chưa có file gộp, hãy trỏ tạm vào file Friday để test
# INPUT_FILE = "../data/raw/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv" 

print(f"🚀 Đang load dữ liệu từ: {INPUT_FILE}...")

try:
    # Load dữ liệu (Chỉ load vài cột quan trọng để chạy cho nhanh nếu máy yếu)
    # Lưu ý: Nếu file quá nặng, thêm tham số nrows=100000 để test trước
    df = pd.read_csv(INPUT_FILE) # Xóa encoding nếu file đã được xử lý sạch ở bước trước
    
    # Chuẩn hóa tên cột lại lần nữa cho chắc (Xóa khoảng trắng)
    df.columns = df.columns.str.strip()
    
    print(f"✅ Dữ liệu đã lên. Kích thước: {df.shape}")
    
    # 1. KIỂM TRA PHÂN BỐ NHÃN (QUAN TRỌNG NHẤT)
    print("\n📊 Thống kê các loại tấn công (Label Distribution):")
    label_counts = df['Label'].value_counts()
    print(label_counts)

    # 2. VẼ BIỂU ĐỒ
    plt.figure(figsize=(12, 6))
    sns.barplot(x=label_counts.index, y=label_counts.values, palette="viridis")
    plt.title("Phân bố số lượng các loại tấn công trong CIC-IDS2017", fontsize=15)
    plt.xlabel("Loại tấn công", fontsize=12)
    plt.ylabel("Số lượng gói tin", fontsize=12)
    plt.xticks(rotation=45, ha='right') # Xoay chữ cho dễ đọc
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Hiển thị số liệu trên cột
    for i, v in enumerate(label_counts.values):
        plt.text(i, v + 100, str(v), ha='center', fontweight='bold')
        
    plt.tight_layout()
    plt.show()

    # 3. KIỂM TRA NULL/INFINITY
    print("\n🔍 Kiểm tra dữ liệu rác:")
    print(f"- Số lượng dòng Null: {df.isna().sum().sum()}")
    
except FileNotFoundError:
    print("❌ LỖI: Không tìm thấy file dữ liệu. Hãy chắc chắn bạn đã chạy data_loader.py hoặc trỏ đúng đường dẫn.")