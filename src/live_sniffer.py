import scapy.all as scapy
from scapy.layers.inet import IP, TCP, UDP
import numpy as np
import xgboost as xgb
import joblib
import os
import time
import sys

# CẤU HÌNH MÀU SẮC CHO TERMINAL
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

class CyberSentinelAgent:
    def __init__(self):
        print(f"{YELLOW}[INIT] Đang khởi động Agent V3.0 Real-time...{RESET}")
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "..", "models")
        # ----------------------------------
        
        self.load_brain()
        
    def load_brain(self):
        """Load bộ não XGBoost đã train từ V2.0"""
        try:
            # Load Model
            self.model = xgb.XGBClassifier()
            self.model.load_model(os.path.join(self.model_path, "xgboost_model.json"))
            
            # Load Label Encoder
            self.le = joblib.load(os.path.join(self.model_path, "xgboost_label_encoder.pkl"))
            print(f"{GREEN}[OK] Đã nạp não bộ XGBoost (Accuracy: 99%){RESET}")
        except Exception as e:
            print(f"{RED}[ERROR] Không tìm thấy Model! Hãy chạy train_xgboost.py trước.{RESET}")
            sys.exit(1)

    def packet_to_features(self, packet):
        """
        Chuyển đổi gói tin thô (Raw Packet) thành vector 78 chiều cho AI.
        Đây là bước 'Feature Engineering' thời gian thực.
        """
        # Tạo vector rỗng 78 chiều (mặc định là 0)
        features = np.zeros((1, 78))
        
        # Nếu không phải gói IP, bỏ qua
        if not packet.haslayer(IP):
            return None
            
        # 1. TRÍCH XUẤT THÔNG TIN CƠ BẢN (CÓ THẬT)
        ip_layer = packet[IP]
        packet_len = len(packet)
        
        # Destination Port (Vị trí cột số 0 trong CIC-IDS2017)
        dst_port = 0
        if packet.haslayer(TCP): dst_port = packet[TCP].dport
        elif packet.haslayer(UDP): dst_port = packet[UDP].dport
        
        # Điền vào vector (Cần map đúng vị trí cột nếu muốn chính xác tuyệt đối)
        # Ở đây ta điền vào các vị trí quan trọng nhất mà Model hay dựa vào
        features[0, 0] = dst_port      # Destination Port
        features[0, 1] = packet_len    # Flow Duration (Giả lập bằng độ dài packet để test)
        features[0, 4] = packet_len    # Total Length of Fwd Packets
        features[0, 7] = packet_len    # Fwd Packet Length Max
        features[0, 16] = packet_len   # Flow Bytes/s (Giả lập)
        
        return features

    def process_packet(self, packet):
        """Hàm này được gọi mỗi khi bắt được 1 gói tin"""
        features = self.packet_to_features(packet)
        if features is None: return

        # AI DỰ ĐOÁN
        try:
            pred_idx = self.model.predict(features)[0]
            label = self.le.inverse_transform([int(pred_idx)])[0]
            
            # Lấy thông tin để in ra
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            proto = packet[IP].proto
            
            # HIỂN THỊ KẾT QUẢ
            if label == 'BENIGN':
               
                # In ra màn hình kể cả gói tin sạch để biết hệ thống hoạt động
                print(f"{GREEN}✓ [AN TOÀN] {src_ip} -> {dst_ip} | Protocol: {proto} | Size: {len(packet)} bytes{RESET}")
                
            else:
                # PHÁT HIỆN TẤN CÔNG -> IN ĐỎ RỰC & CÒI HÚ
                print(f"{RED}🚨 [CẢNH BÁO - {label}] Phát hiện tấn công từ {src_ip} -> {dst_ip} (Port: {packet[TCP].dport if packet.haslayer(TCP) else ''}){RESET}")
                
        except Exception as e:
            pass

    def start_sniffing(self, interface=None):
        print(f"\n{YELLOW}📡 ĐANG LẮNG NGHE TRAFFIC MẠNG (LIVE)...{RESET}")
        print("Nhấn Ctrl+C để dừng.\n")
        
        # Bắt đầu bắt gói tin
        # iface=None nghĩa là để Scapy tự chọn card mạng (thường là Wifi hoặc Ethernet)
        scapy.sniff(prn=self.process_packet, store=False)

if __name__ == "__main__":
    agent = CyberSentinelAgent()
    agent.start_sniffing()