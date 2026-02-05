import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP
import numpy as np
import xgboost as xgb
import joblib
import os
import sys
import subprocess
import ctypes  # Dùng để kiểm tra quyền Admin
import time

# --- CẤU HÌNH MÀU SẮC (CHO NGẦU) ---
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

class CyberEnforcer:
    def __init__(self):
        # 1. KIỂM TRA QUYỀN ADMIN (BẮT BUỘC ĐỂ CHẶN TƯỜNG LỬA)
        if not self.is_admin():
            print(f"{RED}[CRITICAL] V4.0 Cần quyền Administrator để chặn IP!{RESET}")
            print("👉 Hãy chuột phải vào Terminal/VS Code -> Run as Administrator")
            sys.exit(1)

        print(f"{CYAN}╔══════════════════════════════════════════╗{RESET}")
        print(f"{CYAN}║   V4.0 - THE ENFORCER (ACTIVE IPS)       ║{RESET}")
        print(f"{CYAN}╚══════════════════════════════════════════╝{RESET}")
        print(f"{YELLOW}⚡ Chế độ: TỰ ĐỘNG CHẶN (AUTO-BLOCK) KHI PHÁT HIỆN TẤN CÔNG{RESET}")
        
        # 2. LOAD NÃO BỘ (XGBOOST)
        # Fix đường dẫn thông minh như V3
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "..", "models")
        self.load_brain()
        
        self.blocked_ips = set()
        
        # 3. DANH SÁCH TRẮNG (WHITELIST - BẤT KHẢ XÂM PHẠM)
        # AI tuyệt đối không được chặn những IP này dù có nghi ngờ
        self.whitelist = {
            "127.0.0.1",       # Localhost
            "0.0.0.0",
            "192.168.1.1",     # Router Wifi (Thường là dải này)
            "192.168.100.1",   # Gateway dự phòng
            "8.8.8.8",         # Google DNS
            "1.1.1.1",         # Cloudflare DNS
            # Thêm IP máy bạn vào đây nếu biết để tránh tự chặn mình
        }

    def is_admin(self):
        """Kiểm tra xem script có đang chạy quyền Admin không"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def load_brain(self):
        try:
            self.model = xgb.XGBClassifier()
            self.model.load_model(os.path.join(self.model_path, "xgboost_model.json"))
            self.le = joblib.load(os.path.join(self.model_path, "xgboost_label_encoder.pkl"))
            print(f"{GREEN}[SYSTEM] Vũ khí XGBoost: SẴN SÀNG CHIẾN ĐẤU.{RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Không tìm thấy Model tại {self.model_path}!{RESET}")
            sys.exit(1)

    def block_ip(self, ip_address):
        """Hàm THI HÀNH ÁN: Ra lệnh cho Windows Firewall"""
        # 1. Kiểm tra Whitelist
        if ip_address in self.whitelist:
            print(f"{YELLOW}🛡️ [WHITELIST] Bỏ qua cảnh báo với {ip_address} (IP Tin cậy){RESET}")
            return

        # 2. Kiểm tra xem đã chặn chưa (tránh spam lệnh)
        if ip_address in self.blocked_ips:
            return

        print(f"{RED}🚫 [BLOCKING] Đang thi hành lệnh chặn IP: {ip_address}...{RESET}")
        
        # 3. Gọi lệnh CMD chặn tường lửa (Block Inbound)
        rule_name = f"CyberSentinel_Block_{ip_address}"
        command = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={ip_address}'
        
        try:
            # Chạy lệnh ngầm (ẩn cửa sổ popup)
            subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL)
            print(f"{RED}🔥🔥 ĐÃ TIÊU DIỆT KẾT NỐI TỪ {ip_address}! (Added to Firewall){RESET}")
            self.blocked_ips.add(ip_address)
        except Exception as e:
            print(f"{YELLOW}⚠️ Lỗi chặn tường lửa: {e}{RESET}")

    def packet_to_features(self, packet):
        """Trích xuất đặc trưng (Giống V3.0)"""
        features = np.zeros((1, 78))
        if not packet.haslayer(IP): return None
        
        packet_len = len(packet)
        dst_port = 0
        if packet.haslayer(TCP): dst_port = packet[TCP].dport
        elif packet.haslayer(UDP): dst_port = packet[UDP].dport
        
        features[0, 0] = dst_port
        features[0, 1] = packet_len
        features[0, 4] = packet_len
        features[0, 7] = packet_len
        features[0, 16] = packet_len
        return features

    def process_packet(self, packet):
        features = self.packet_to_features(packet)
        if features is None: return

        try:
            pred_idx = self.model.predict(features)[0]
            label = self.le.inverse_transform([int(pred_idx)])[0]
            src_ip = packet[IP].src
            
            if label == 'BENIGN':
                # Im lặng là vàng (Chế độ sát thủ không nói nhiều)
                pass 
            else:
                # PHÁT HIỆN -> CHẶN NGAY LẬP TỨC
                print(f"\n{RED}🚨 [PHÁT HIỆN TẤN CÔNG - {label}] Mục tiêu: {src_ip}{RESET}")
                self.block_ip(src_ip)
                
        except Exception as e:
            pass

    def start(self):
        print(f"{YELLOW}📡 Đang quét mạng... (Nhấn Ctrl+C để dừng){RESET}")
        scapy.sniff(prn=self.process_packet, store=False)

if __name__ == "__main__":
    enforcer = CyberEnforcer()
    enforcer.start()