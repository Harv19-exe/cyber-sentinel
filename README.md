# 🛡️ CYBER SENTINEL: AI-Powered IDS/IPS & SOC System

> **Hệ thống Phát hiện & Ngăn chặn Xâm nhập Mạng sử dụng AI (XGBoost) và Real-time Sniffing.**
> *Dự án từ đồ án sinh viên phát triển lên hệ thống SOC thu nhỏ (V5.0).*

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![AI Model](https://img.shields.io/badge/Model-XGBoost-orange.svg)
![Security](https://img.shields.io/badge/Security-IDS%2FIPS-red.svg)
![Status](https://img.shields.io/badge/Status-V5.0%20God%20Mode-brightgreen.svg)

---

## 🌟 Giới thiệu (Overview)
**Cyber Sentinel** là một giải pháp an ninh mạng toàn diện. Không chỉ phân tích dữ liệu tĩnh (CSV), hệ thống còn có khả năng bắt gói tin thời gian thực (Real-time Sniffing), sử dụng trí tuệ nhân tạo để phân loại tấn công với độ chính xác **99.98%**, và tự động phản ứng lại các mối đe dọa.

## 🚀 Lộ trình phát triển (Versions History)

Dự án được quy hoạch thành các phiên bản (Branch) riêng biệt để phục vụ các mục đích khác nhau:

| Phiên bản | Nhánh Git (Branch) | Trạng thái | Tính năng nổi bật |
| :--- | :--- | :--- | :--- |
| **V1.0 (Legacy)** | `tag: v1.0` | 🔒 Lưu trữ | Sử dụng Pandas & Random Forest. Bản thử nghiệm đầu tiên. |
| **V2.0 (Enterprise)** | `tag: v2.0` | 🔒 Lưu trữ | Nâng cấp lên Polars & XGBoost. Tối ưu tốc độ xử lý dữ liệu lớn. |
| **V3.0 (Real-time)** | `main-v3.0-realtime` | ✅ **Ổn định** | **Chế độ quan sát (Passive Mode).** Bắt gói tin sống, cảnh báo trên màn hình. An toàn để Demo. |
| **V4.0 (Enforcer)** | `v4.0-ips` | ⚔️ **Nâng cao** | **Chế độ thực thi (Active IPS).** Tự động chặn IP tấn công bằng Windows Firewall. |
| **V5.0 (God Mode)** | `v5.0-god-mode` | 👑 **Cao cấp** | **Hệ thống SOC thu nhỏ.** Bao gồm V4 + Tích hợp **Telegram Bot** báo cáo từ xa + **XAI** giải thích lý do chặn. |

---

## 🛠️ Cài đặt (Installation)

### 1. Yêu cầu hệ thống
* Python 3.8+
* Hệ điều hành: Windows (Khuyến nghị để dùng tính năng Firewall Block)
* **Npcap:** Bắt buộc cài đặt để bắt gói tin ([Tải tại đây](https://npcap.com/)). *Lưu ý chọn "Install in WinPcap API-compatible Mode".*

### 2. Cài đặt thư viện
```bash
pip install scapy xgboost pandas numpy scikit-learn requests joblib polars




##Hướng dẫn sử dụng (Usage)
1. Chạy bản V3.0 (Quan sát - An toàn)
Bash
git checkout main-v3.0-realtime
python src/live_sniffer.py
Mô tả: Màn hình sẽ hiển thị lưu lượng mạng thời gian thực. Cảnh báo ĐỎ khi thấy tấn công. Không can thiệp hệ thống.

2. Chạy bản V5.0 (SOC System - Full tính năng)
Bash
git checkout v5.0-god-mode
# BẮT BUỘC CHẠY VỚI QUYỀN ADMINISTRATOR
python src/soc_system.py
Mô tả:

Hệ thống chạy ngầm, tự động chặn IP độc hại.

Gửi tin nhắn cảnh báo về điện thoại qua Telegram.

AI giải thích lý do chặn.





##Công nghệ lõi (Tech Stack)
Core Engine: Python

Network Sniffer: Scapy Library

AI/ML Model: XGBoost (eXtreme Gradient Boosting) - Acc: 99.98%

Data Processing: Polars (High Performance)

Integration: Telegram Bot API, Windows Advanced Firewall API (Netsh)
