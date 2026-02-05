import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP
import numpy as np
import xgboost as xgb
import joblib
import os
import sys
import subprocess
import ctypes
import time
import requests
import threading
from datetime import datetime

# ==============================================================================
# CẤU HÌNH 
# ==============================================================================
TELEGRAM_BOT_TOKEN = "8508919854:AAFmedRnJKVHQ1_-UCeMhzLxA5AuL79aFg0" 
TELEGRAM_CHAT_ID = "8447991224"
# ==============================================================================

# MÀU SẮC GIAO DIỆN
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

class CyberGodMode:
    def __init__(self):
        # 1. KIỂM TRA QUYỀN ADMIN (BẮT BUỘC ĐỂ CHẶN FIREWALL)
        if not self.is_admin():
            print(f"{RED}[CRITICAL] V5.0 Cần quyền Administrator để chặn IP!{RESET}")
            print(f"{YELLOW}👉 Hãy chuột phải vào Terminal -> Run as Administrator{RESET}")
            sys.exit(1)

        print(f"{MAGENTA}╔═══════════════════════════════════════════════════════╗{RESET}")
        print(f"{MAGENTA}║   V5.0 - CYBER SENTINEL: GOD MODE (SOC SYSTEM)        ║{RESET}")
        print(f"{MAGENTA}╚═══════════════════════════════════════════════════════╝{RESET}")
        print(f"{YELLOW}⚡ Features: IPS Firewall (V4) + Telegram Alert (V5) + AI Explain{RESET}")
        
        # 2. LOAD AI MODEL
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "..", "models")
        self.load_brain()
        
        self.blocked_ips = set()
        
        # 3. WHITELIST 
        self.whitelist = {
            "127.0.0.1", "0.0.0.0", "192.168.1.1", "192.168.100.1",
            "8.8.8.8", "1.1.1.1",
            # IP máy bạn (tránh tự chặn mình)
        }

        # Gửi tin nhắn test khi khởi động
        self.send_telegram_async("🚀 **HỆ THỐNG SOC V5 ĐÃ KÍCH HOẠT!**\nSẵn sàng bảo vệ máy chủ.")

    def is_admin(self):
        try: return ctypes.windll.shell32.IsUserAnAdmin()
        except: return False

    def load_brain(self):
        try:
            self.model = xgb.XGBClassifier()
            self.model.load_model(os.path.join(self.model_path, "xgboost_model.json"))
            self.le = joblib.load(os.path.join(self.model_path, "xgboost_label_encoder.pkl"))
            print(f"{GREEN}[SYSTEM] AI Engine & IPS Module: Loaded.{RESET}")
        except: 
            print(f"{RED}[ERROR] Không tìm thấy Model tại {self.model_path}!{RESET}")
            sys.exit(1)

    # --- MODULE TELEGRAM (ĐA LUỒNG - KHÔNG LAG) ---
    def send_telegram_async(self, message):
        """Gửi tin nhắn trong luồng riêng để hệ thống chính vẫn bắt gói tin mượt mà"""
        def worker():
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                data = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
                requests.post(url, data=data, timeout=5)
            except Exception as e:
                print(f"{YELLOW}⚠️ Lỗi gửi Telegram: {e}{RESET}")
        
        t = threading.Thread(target=worker)
        t.start()

    # --- MODULE GIẢI THÍCH (XAI) ---
    def explain_attack(self, features, ip, port):
        packet_len = features[0, 1]
        reason = f"Kết nối Port {int(port)}. "
        if packet_len < 10: reason += "Gói tin quá nhỏ (Dấu hiệu Scan/Bot)."
        elif packet_len > 1200: reason += "Gói tin quá lớn (Dấu hiệu DoS/Flood)."
        else: reason += "Hành vi bất thường khớp với mẫu tấn công."
        return reason

    # --- MODULE CHẶN & BÁO CÁO (KẾ THỪA V4) ---
    def block_and_report(self, ip_address, attack_type, explanation):
        # Kiểm tra Whitelist
        if ip_address in self.whitelist or ip_address in self.blocked_ips: return

        print(f"{RED}🚫 [IPS ACTIVE] Đang chặn {ip_address}...{RESET}")
        
        # 1. THỰC THI CHẶN FIREWALL (SỨC MẠNH V4)
        rule_name = f"CyberSentinel_Block_{ip_address}"
        cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip_address}'
        
        try:
            # Chạy lệnh ngầm
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL)
            self.blocked_ips.add(ip_address)
            print(f"{RED}🔥🔥 ĐÃ TIÊU DIỆT KẾT NỐI!{RESET}")
            
            # 2. BÁO CÁO NGAY LẬP TỨC (SỨC MẠNH V5)
            print(f"{CYAN}   -> 📨 Đang báo cáo sếp (Telegram)...{RESET}")
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            msg = (f"🚨 **PHÁT HIỆN TẤN CÔNG!**\n"
                   f"⏰ `{timestamp}`\n"
                   f"💀 **IP:** `{ip_address}`\n"
                   f"🔫 **Loại:** {attack_type}\n"
                   f"🛡️ **Hành động:** Đã chặn Firewall (IPS)\n"
                   f"🔍 **Lý do:** {explanation}")
            
            self.send_telegram_async(msg)
            
        except Exception as e:
            print(f"{YELLOW}Lỗi chặn Firewall: {e}{RESET}")

    def process_packet(self, packet):
        # Trích xuất đặc trưng 78 chiều (Simplified)
        features = np.zeros((1, 78))
        if not packet.haslayer(IP): return None
        
        packet_len = len(packet)
        dst_port = 0
        if packet.haslayer(TCP): dst_port = packet[TCP].dport
        elif packet.haslayer(UDP): dst_port = packet[UDP].dport
        
        features[0, 0] = dst_port; features[0, 1] = packet_len
        features[0, 4] = packet_len; features[0, 7] = packet_len; features[0, 16] = packet_len

        try:
            # AI Dự đoán
            pred_idx = self.model.predict(features)[0]
            label = self.le.inverse_transform([int(pred_idx)])[0]
            src_ip = packet[IP].src
            
            if label != 'BENIGN':
                # Quy trình: Giải thích -> Chặn -> Báo cáo
                explanation = self.explain_attack(features, src_ip, dst_port)
                print(f"\n{RED}🚨 [DETECTED - {label}] Mục tiêu: {src_ip}{RESET}")
                self.block_and_report(src_ip, label, explanation)
                
        except: pass

    def start(self):
        print(f"{YELLOW}📡 SOC Đang quét mạng... (Check điện thoại đi sếp!){RESET}")
        scapy.sniff(prn=self.process_packet, store=False)

if __name__ == "__main__":
    soc = CyberGodMode()
    soc.start()