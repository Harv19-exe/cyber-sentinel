# 🛡️ CYBER SENTINEL - AI-Powered Intrusion Detection System

Hệ thống phát hiện xâm nhập mạng (IDS) thế hệ mới, tích hợp kiến trúc lai ghép giữa **Machine Learning (Random Forest)** và **Deep Learning (ANN)** để phát hiện các cuộc tấn công mạng trong thời gian thực.

![Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Tech](https://img.shields.io/badge/AI-TensorFlow%20%7C%20Scikit--Learn-orange)

## 🚀 Tính năng nổi bật
* **Đa mô hình (Hybrid AI):** Tùy chọn linh hoạt giữa tốc độ (Random Forest) và độ chính xác chuyên sâu (Deep Learning).
* **Xử lý mất cân bằng dữ liệu:** Tích hợp kỹ thuật **Class Weights**, nâng cao khả năng phát hiện Botnet từ 0% lên 44%.
* **Interactive Dashboard:** Giao diện Streamlit trực quan, cảnh báo thời gian thực.
* **Smart Sampling:** Thuật toán lấy mẫu thông minh giúp phân tích file log GB mà không tràn RAM.

## 📂 Cấu trúc dự án
```text
CYBER-SENTINEL/
├── app/                # Source code giao diện (Streamlit)
├── data/               # Thư mục chứa dữ liệu (Raw & Processed)
├── models/             # Các model AI đã huấn luyện (.pkl, .keras)
├── notebooks/          # Jupyter Notebook phân tích EDA
├── src/                # Mã nguồn lõi (Training, Preprocessing)
└── requirements.txt    # Danh sách thư viện