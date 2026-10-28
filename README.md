# 🏠 Hệ Thống Mô Phỏng IoT Giám Sát Điện Năng Tiêu Thụ Trong Gia Đình

Dự án mô phỏng hoàn chỉnh 100% không cần phần cứng thật, sử dụng **Python + Mosquitto MQTT + Node-RED + MySQL**.

---

## 🚀 Cách Khởi Chạy Nhanh (1-Click)

1. Nháy đúp vào file [`start_all.bat`](./start_all.bat) để tự động bật cả 4 dịch vụ:
   - **MQTT Broker:** `mqtt://127.0.0.1:1883`
   - **MySQL Server (`smart_energy_db`):** `127.0.0.1:3306`
   - **Node-RED Flow Editor:** `http://127.0.0.1:1880`
   - **Node-RED Dashboard (Giao diện chính):** `http://127.0.0.1:1880/ui`

---

## 📂 Cấu Trúc Thư Mục Dự Án

```
iot-energy-monitor/
├── simulator/
│   └── sensor_simulator.py     # Trình mô phỏng Python (ESP32 + 4x PZEM-004T + Relay)
├── mosquitto/
│   └── mosquitto.conf          # File cấu hình chuẩn của Eclipse Mosquitto Broker
├── database/
│   ├── schema.sql              # File thiết kế bảng MySQL (energy_logs, alert_logs)
│   └── smart_energy_db.sqlite  # File lưu trữ dữ liệu bền vững cho MySQL Server cục bộ
├── nodered_data/
│   ├── flows.json              # Toàn bộ sơ đồ khối Node-RED & giao diện Dashboard
│   ├── flows_cred.json         # Cấu hình tài khoản kết nối MySQL (root)
│   └── settings.js             # Cấu hình khởi động Node-RED
├── services/
│   ├── mqtt_broker.js          # Dịch vụ MQTT Broker lắng nghe cổng 1883
│   └── mysql_server.py         # Dịch vụ MySQL Server lắng nghe cổng 3306
├── docker-compose.yml          # Cấu hình chạy bằng Docker (Tùy chọn)
└── start_all.bat               # Script khởi động toàn bộ hệ thống với 1 cú nhấp chuột
```

---

## 🔄 Luồng Hoạt Động Của Hệ Thống

1. **Chiều Giám Sát (Sensor ➔ MQTT ➔ Node-RED ➔ Dashboard & MySQL):**
   - Mỗi 2 giây, [`sensor_simulator.py`](./simulator/sensor_simulator.py) sinh dữ liệu điện năng thực tế ($U, I, P, E, \cos\phi, f$, công suất từng phòng và tiền điện bậc thang EVN) rồi gửi (`PUBLISH`) lên topic `home/energy/telemetry`.
   - **Node-RED** nhận gói tin qua node `mqtt in`, tách dữ liệu hiển thị lên đồng hồ Gauge, đồ thị đường (`Line Chart`), biểu đồ tròn (`Pie Chart`) và kiểm tra ngưỡng cảnh báo.
   - Định kỳ mỗi 6 giây (hoặc ngay khi xảy ra quá tải/sụt áp), Node-RED thực thi lệnh `INSERT INTO energy_logs` lưu vào **MySQL** (`127.0.0.1:3306`) và tự động cập nhật bảng lịch sử trên Dashboard.

2. **Chiều Điều Khiển (Dashboard ➔ Node-RED ➔ MQTT ➔ Python Simulator):**
   - Khi người dùng gạt công tắc **Aptomat Tổng (ON/OFF)** hoặc chọn **Kịch bản tải (Bình thường / Quá tải >3.3kW / Sụt áp <195V / Ban đêm)** trên Dashboard, Node-RED gửi lệnh JSON qua topic `home/energy/control`.
   - [`sensor_simulator.py`](./simulator/sensor_simulator.py) nhận lệnh (`SUBSCRIBE`) và thay đổi ngay trạng thái đóng/cắt điện hoặc kịch bản tải tức thời.
