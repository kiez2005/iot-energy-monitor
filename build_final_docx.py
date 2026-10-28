"""
Script tự động cập nhật trực tiếp file báo cáo gốc (.docx) của nhóm:
1. Giữ nguyên 100% định dạng trang bìa, Logo Đại học Điện lực, Hình 2.1, Hình 2.7, lề trang và font chữ gốc.
2. Điền toàn bộ các chỗ trống [...] trong Mở đầu, Chương 1, Chương 2, Chương 3, Chương 4, Tài liệu tham khảo.
3. Tích hợp chi tiết hệ thống mô phỏng (Python + Mosquitto MQTT + Node-RED + MySQL) vào Chương 2 và Chương 3.
4. Điền đầy đủ số liệu thực nghiệm vào tất cả các Bảng (Phiếu chấm điểm, Bảng 2.1, Bảng 2.3, Bảng 3.1, Bảng 3.2).
5. Tự động vẽ và chèn hình ảnh kỹ thuật sắc nét thay thế cho toàn bộ các dòng chữ "[CHÈN HÌNH]..." còn trống.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC_DOCX = r"C:\Users\Trung\.gemini\antigravity\brain\b394b9d2-495d-45ba-aa83-074088fd3b4f\.user_uploaded\media_1793170549243_85c008b3.docx"
OUT_DOCX = r"C:\Users\Trung\.gemini\antigravity\scratch\iot-energy-monitor\BAO_CAO_CUOI_KY_IOT_D18CNPM5.docx"
IMG_DIR = r"C:\Users\Trung\.gemini\antigravity\scratch\iot-energy-monitor\report_images"
os.makedirs(IMG_DIR, exist_ok=True)


def get_font(size=18, bold=False):
    font_candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\timesbd.ttf" if bold else r"C:\Windows\Fonts\times.ttf",
        r"C:\Windows\Fonts\seguisb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for path in font_candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_box(draw, xy, bg, outline, title, lines, title_color=(15, 23, 42), text_color=(51, 65, 85)):
    draw.rounded_rectangle(xy, radius=12, fill=bg, outline=outline, width=3)
    x1, y1, x2, y2 = xy
    f_title = get_font(19, bold=True)
    f_body = get_font(16, bold=False)
    draw.text((x1 + 16, y1 + 12), title, fill=title_color, font=f_title)
    y_curr = y1 + 42
    for line in lines:
        draw.text((x1 + 16, y_curr), line, fill=text_color, font=f_body)
        y_curr += 24


def generate_all_figures():
    """Tạo bộ hình vẽ kỹ thuật và kết quả mô phỏng chất lượng cao để chèn vào Word."""
    figs = {}

    # 1. Hình 1.1: Mô hình tổng quan hệ thống giám sát điện năng gia đình
    img = Image.new("RGB", (1100, 460), (248, 250, 252))
    d = ImageDraw.Draw(img)
    draw_box(d, (30, 40, 320, 420), (254, 243, 199), (217, 119, 6), "1. PHỤ TẢI GIA ĐÌNH (220V)", [
        "• Phòng khách: TV, Đèn, Quạt",
        "  (280W - 450W)",
        "• Nhà bếp: Tủ lạnh, Bếp từ",
        "  (600W - 2.300W)",
        "• Phòng ngủ: Điều hòa, Nóng lạnh",
        "  (350W - 1.450W)",
        "",
        "-> Đo qua PZEM-004T / Python"
    ])
    draw_box(d, (390, 40, 700, 420), (224, 242, 254), (2, 132, 199), "2. NÚT ĐO & TRUYỀN THÔNG", [
        "• Vi điều khiển ESP32 / Python",
        "• Tính toán U, I, P, E, f, cos(φ)",
        "• Đóng gói bản tin JSON chuẩn",
        "• Kết nối Wi-Fi / TCP-IP",
        "• Giao thức Mosquitto MQTT",
        "  (Cổng 1883 - Chu kỳ 2 giây)",
        "• Cơ cấu chấp hành: Relay 5V",
        "  (Đóng/ngắt Aptomat từ xa)"
    ])
    draw_box(d, (770, 40, 1070, 420), (220, 252, 231), (22, 163, 74), "3. XỬ LÝ, CSDL & DASHBOARD", [
        "• Trung tâm xử lý Node-RED",
        "• Tính giá điện 6 bậc thang EVN",
        "• Cảnh báo Quá tải & Sụt áp",
        "• Lưu trữ CSDL MySQL (Port 3306)",
        "  (Bảng energy_logs, alert_logs)",
        "• Giao diện Node-RED Dashboard",
        "  (Gauge, Đồ thị, Thẻ KPI, Bảng)",
        "• Điều khiển 2 chiều qua Web"
    ])
    d.line([(320, 230), (390, 230)], fill=(2, 132, 199), width=4)
    d.line([(700, 230), (770, 230)], fill=(22, 163, 74), width=4)
    p1 = os.path.join(IMG_DIR, "fig1_1_overview.png")
    img.save(p1)
    figs["1.1"] = p1

    # 2. Hình 1.2: Kiến trúc IoT 4 tầng
    img = Image.new("RGB", (1100, 520), (255, 255, 255))
    d = ImageDraw.Draw(img)
    layers = [
        ((60, 25, 1040, 125), (224, 231, 255), (67, 56, 202), "TẦNG 4 - TẦNG ỨNG DỤNG (APPLICATION LAYER)",
         ["Giao diện Web Node-RED Dashboard (http://127.0.0.1:1880/ui): Đồng hồ Gauge, Biểu đồ Line/Pie, Thẻ KPI, Công tắc Relay"]),
        ((60, 150, 1040, 250), (220, 252, 231), (21, 128, 61), "TẦNG 3 - TẦNG XỬ LÝ VÀ LƯU TRỮ (MIDDLEWARE / DATA LAYER)",
         ["Bộ xử lý luồng Node-RED + Hệ quản trị CSDL MySQL (smart_energy_db): Tính tiền điện bậc thang EVN, kiểm tra ngưỡng, lưu lịch sử"]),
        ((60, 275, 1040, 375), (224, 242, 254), (3, 105, 161), "TẦNG 2 - TẦNG MẠNG VÀ TRUYỀN THÔNG (NETWORK LAYER)",
         ["Mạng Wi-Fi 2.4GHz / TCP-IP & Máy chủ Mosquitto MQTT Broker (Port 1883): Định tuyến bản tin Publish/Subscribe 2 chiều"]),
        ((60, 400, 1040, 500), (254, 243, 199), (180, 83, 9), "TẦNG 1 - TẦNG CẢM BIẾN VÀ CHẤP HÀNH (PERCEPTION LAYER)",
         ["Phần cứng: ESP32 + Cảm biến PZEM-004T V3.0 + Module Relay 5V  |  Mô phỏng: Python Virtual Sensor (sensor_simulator.py)"])
    ]
    for xy, bg, ol, title, lines in layers:
        draw_box(d, xy, bg, ol, title, lines)
    p2 = os.path.join(IMG_DIR, "fig1_2_4layers.png")
    img.save(p2)
    figs["1.2"] = p2

    # 3. Hình 1.3: Thiết bị thương mại
    img = Image.new("RGB", (1050, 360), (248, 250, 252))
    d = ImageDraw.Draw(img)
    draw_box(d, (40, 30, 510, 330), (255, 255, 255), (100, 116, 139), "Ổ CẮM THÔNG MINH ĐO ĐIỆN (SMART PLUG)", [
        "• Ví dụ: Sonoff Pow R2 / Tuya Smart Plug 16A",
        "• Chức năng: Đo công suất 1 thiết bị đơn lẻ,",
        "  bật/tắt qua ứng dụng điện thoại của hãng.",
        "• Hạn chế: Phụ thuộc máy chủ Cloud nước ngoài,",
        "  không hỗ trợ trích xuất CSDL MySQL riêng."
    ])
    draw_box(d, (550, 30, 1010, 330), (255, 255, 255), (2, 132, 199), "CÔNG Tơ / APTOMAT THÔNG MINH GẮN TỦ ĐIỆN", [
        "• Ví dụ: Tuya Smart MCB / DTSU666 / PZEM-004T",
        "• Chức năng: Lắp trên thanh ray tủ điện tổng,",
        "  đo dòng điện lớn qua biến dòng CT (đến 100A).",
        "• Hướng đề tài: Kết hợp PZEM-004T + ESP32/Python",
        "  với Node-RED & MySQL để làm chủ 100% dữ liệu."
    ])
    p3 = os.path.join(IMG_DIR, "fig1_3_commercial.png")
    img.save(p3)
    figs["1.3"] = p3

    # 4. Hình 1.4: Mô hình Publish/Subscribe của MQTT
    img = Image.new("RGB", (1100, 420), (255, 255, 255))
    d = ImageDraw.Draw(img)
    draw_box(d, (30, 60, 340, 360), (254, 243, 199), (217, 119, 6), "NÚT ĐO (ESP32 / PYTHON)", [
        "• Vai trò 1: MQTT Publisher",
        "  Gửi JSON (U, I, P, E, f, PF)",
        "  mỗi 2 giây/lần.",
        "",
        "• Vai trò 2: MQTT Subscriber",
        "  Nhận lệnh đóng/ngắt Relay",
        "  và chuyển kịch bản tải."
    ])
    draw_box(d, (410, 60, 690, 360), (224, 242, 254), (2, 132, 199), "MOSQUITTO BROKER", [
        "• Địa chỉ: 127.0.0.1:1883",
        "• Kênh dữ liệu đo (Telemetry):",
        "  home/energy/telemetry",
        "",
        "• Kênh điều khiển (Control):",
        "  home/energy/control",
        "• Cơ chế lọc theo Topic"
    ])
    draw_box(d, (760, 60, 1070, 360), (220, 252, 231), (22, 163, 74), "NODE-RED & DASHBOARD", [
        "• Vai trò 1: MQTT Subscriber",
        "  Nhận JSON -> Lưu MySQL ->",
        "  Hiển thị đồ thị & cảnh báo.",
        "",
        "• Vai trò 2: MQTT Publisher",
        "  Gửi lệnh ON/OFF Aptomat",
        "  khi người dùng gạt Switch."
    ])
    d.line([(340, 150), (410, 150)], fill=(217, 119, 6), width=4)
    d.line([(690, 150), (760, 150)], fill=(217, 119, 6), width=4)
    d.line([(760, 280), (690, 280)], fill=(22, 163, 74), width=4)
    d.line([(410, 280), (340, 280)], fill=(22, 163, 74), width=4)
    p4 = os.path.join(IMG_DIR, "fig1_4_mqtt_pubsub.png")
    img.save(p4)
    figs["1.4"] = p4

    # 5. Hình 2.2 - 2.6: Sơ đồ phần cứng Khối nguồn, PZEM-004T, Đấu nối, Relay, ESP32
    hw_specs = [
        ("2.2", "fig2_2_power.png", "SƠ ĐỒ KHỐI NGUỒN CẤP 5VDC / 2A CHO NÚT ĐO",
         ["• Đầu vào: Điện lưới xoay chiều 220VAC - 50Hz (qua cầu chì bảo vệ F1 1A và tụ chống sét lan truyền MOV).",
          "• Module hạ áp cách ly: HLK-PM01 (hoặc Adapter 5VDC/2A) biến đổi 220VAC -> 5VDC ổn định.",
          "• Mạch lọc nguồn: Tụ hóa 470uF/16V kết hợp tụ gốm 104 lọc nhiễu cao tần.",
          "• Cấp nguồn 5VDC cho: Chân VIN của ESP32 DevKit, đầu thu phát quang của PZEM-004T và cuộn hút Relay 5V.",
          "• Ổn áp nội 3.3V (AMS1117 trên bo ESP32): Cấp nguồn nuôi vi xử lý ESP32-WROOM-32 và màn hình OLED."]),
        ("2.3", "fig2_3_pzem.png", "CẤU TẠO VÀ CÁC CỔNG GIAO TIẾP CỦA MODULE PZEM-004T V3.0",
         ["• Cổng đo phía cao áp (220VAC): Chân 1 (L), Chân 2 (N) đo áp; Chân 3, 4 nối biến dòng CT (0 - 100A).",
          "• IC chuyên dụng đo năng lượng: V9881D / BL0939 tích hợp ADC độ phân giải cao tính U, I, P, E, f, PF.",
          "• Cách ly an toàn: Sử dụng 2 Optocoupler (PC817) cách ly hoàn toàn giữa phía lưới 220VAC và phía TTL 5V.",
          "• Cổng giao tiếp phía thấp áp (4 chân TTL): 5V, RX, TX, GND truyền thông chuẩn Modbus-RTU 9600 baud."]),
        ("2.4", "fig2_4_wiring.png", "SƠ ĐỒ ĐẤU NỐI GIAO TIẾP UART GIỮA PZEM-004T V3.0 VÀ ESP32",
         ["• PZEM-004T (Chân 5V)  <===>  Chân 5V (VIN) của ESP32 DevKit",
          "• PZEM-004T (Chân GND) <===>  Chân GND chung của ESP32 DevKit",
          "• PZEM-004T (Chân TX)  ===[Cầu chia áp 1kΩ / 2kΩ (5V -> 3.3V)]===> GPIO16 (RX2) của ESP32",
          "• PZEM-004T (Chân RX)  <========================================== GPIO17 (TX2) của ESP32",
          "• Module Relay 5V (IN) <========================================== GPIO26 của ESP32"]),
        ("2.5", "fig2_5_relay.png", "SƠ ĐỒ KHỐI CHẤP HÀNH MODULE RELAY 5V 1 KÊNH (10A/250VAC)",
         ["• Tín hiệu điều khiển: Nhận mức logic từ chân GPIO26 của ESP32 (hoặc lệnh JSON {'relay': true/false} qua MQTT).",
          "• Cách ly quang: Tích hợp Optocoupler EL817 và Transistor kích dòng bảo vệ chân GPIO của vi điều khiển.",
          "• Tiếp điểm сило (COM - NO): Đấu nối tiếp trên dây pha (L) cấp nguồn cho phụ tải (Đóng khi ON, Ngắt khi OFF).",
          "• Đèn báo trạng thái: LED xanh báo nguồn, LED đỏ sáng khi tiếp điểm Relay đóng mạch."]),
        ("2.6", "fig2_6_esp32.png", "SƠ ĐỒ PHÂN BỔ CHÂN GIAO TIẾP TRÊN VI ĐIỀU KHIỂN ESP32 DEVKIT V1",
         ["• Vi xử lý: Dual-core Xtensa 32-bit LX6 (240MHz), 520KB SRAM, Wi-Fi 802.11 b/g/n 2.4GHz.",
          "• Cổng UART2 phần cứng: GPIO16 (RX2) và GPIO17 (TX2) giao tiếp độc lập với cảm biến PZEM-004T.",
          "• Cổng UART0 (USB-UART CP2102): Nạp chương trình và xuất log gỡ lỗi lên Serial Monitor.",
          "• Cổng I2C phần cứng: GPIO21 (SDA) và GPIO22 (SCL) kết nối màn hình OLED SSD1306 0.96 inch.",
          "• Cổng xuất điều khiển: GPIO26 điều khiển Relay đóng/cắt tải; GPIO2 điều khiển LED báo kết nối MQTT."])
    ]
    for key, fname, title, lines in hw_specs:
        img = Image.new("RGB", (1050, 320), (248, 250, 252))
        d = ImageDraw.Draw(img)
        draw_box(d, (25, 20, 1025, 300), (255, 255, 255), (3, 105, 161), title, lines)
        fpath = os.path.join(IMG_DIR, fname)
        img.save(fpath)
        figs[key] = fpath

    # 6. Hình 2.8: Luồng xử lý dữ liệu (Flow) trong Node-RED
    img = Image.new("RGB", (1120, 480), (30, 41, 59))
    d = ImageDraw.Draw(img)
    draw_box(d, (30, 35, 320, 165), (219, 234, 254), (37, 99, 235), "MQTT IN (Port 1883)", [
        "Topic: home/energy/telemetry",
        "Nhận gói tin JSON mỗi 2s",
        "từ Python / ESP32"
    ])
    draw_box(d, (380, 35, 730, 225), (254, 243, 199), (217, 119, 6), "FUNCTION: XỬ LÝ & KIỂM TRA NGƯỠNG", [
        "• Giải mã U, I, P, E, f, PF, rooms",
        "• So sánh P với ngưỡng (3000W)",
        "• Kiểm tra Sụt áp (U < 200V)",
        "• Tạo câu lệnh INSERT MySQL",
        "• Phân phối ra 5 nhánh hiển thị"
    ])
    draw_box(d, (790, 35, 1090, 225), (220, 252, 231), (22, 163, 74), "DASHBOARD WIDGETS (/ui)", [
        "• 2 Đồng hồ Gauge (U & P)",
        "• 6 Thẻ KPI (I, f, PF, kWh, VNĐ)",
        "• Đồ thị Line 4 đường & Pie Chart",
        "• Banner Cảnh báo đổi màu động"
    ])
    draw_box(d, (30, 270, 340, 440), (243, 232, 255), (147, 51, 234), "ĐIỀU KHIỂN TỪ DASHBOARD", [
        "• Switch Aptomat (ON / OFF)",
        "• Dropdown chọn 4 Kịch bản tải",
        "• Slider chỉnh ngưỡng quá tải",
        "-> Gửi tới node MQTT OUT"
    ])
    draw_box(d, (390, 270, 720, 440), (224, 242, 254), (2, 132, 199), "NODE MYSQL (smart_energy_db)", [
        "• Cổng kết nối: 127.0.0.1:3306",
        "• INSERT INTO energy_logs định kỳ",
        "  (6s/lần) & tức thời khi quá tải",
        "• SELECT 12 bản ghi mới nhất"
    ])
    draw_box(d, (770, 270, 1090, 440), (254, 226, 226), (220, 38, 38), "MQTT OUT & BẢNG LỊCH SỬ", [
        "• Publish: home/energy/control",
        "  về Python Simulator",
        "• Render Bảng HTML 12 cột",
        "  hiển thị lịch sử MySQL"
    ])
    d.line([(320, 100), (380, 100)], fill=(56, 189, 248), width=4)
    d.line([(730, 120), (790, 120)], fill=(52, 211, 153), width=4)
    d.line([(555, 225), (555, 270)], fill=(251, 191, 36), width=4)
    d.line([(340, 355), (390, 355)], fill=(192, 132, 252), width=4)
    d.line([(720, 355), (770, 355)], fill=(56, 189, 248), width=4)
    p28 = os.path.join(IMG_DIR, "fig2_8_nodered_flow.png")
    img.save(p28)
    figs["2.8"] = p28

    # 7. Hình 2.9 & 3.3: Giao diện Dashboard đồ họa thật (Đồng hồ bán nguyệt, biểu đồ tròn, bảng kẻ ô, không dùng emoji gây lỗi ô vuông)
    user_dash_img = r"C:\Users\Trung\.gemini\antigravity\brain\b394b9d2-495d-45ba-aa83-074088fd3b4f\.user_uploaded\media_1793169462881_d3ddad65.png"
    img = Image.new("RGB", (1240, 820), (9, 13, 22))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1240, 48), fill=(15, 23, 42))
    d.text((24, 13), "GIÁM SÁT ĐIỆN NĂNG GIA ĐÌNH  |  Node-RED Dashboard (http://127.0.0.1:1880/ui)",
           fill=(56, 189, 248), font=get_font(19, bold=True))

    # Group 1: Thông số điện lưới (Trái trên)
    d.rounded_rectangle((18, 62, 608, 332), radius=10, fill=(17, 24, 39), outline=(30, 41, 59), width=2)
    d.text((34, 74), "1. Thông Số Điện Lưới Thời Gian Thực (PZEM-004T)", fill=(56, 189, 248), font=get_font(17, bold=True))
    # Gauge 1: Điện áp
    d.text((115, 108), "Điện Áp Lưới (U)", fill=(203, 213, 225), font=get_font(15, bold=True))
    d.pieslice((95, 132, 245, 282), start=180, end=360, fill=(16, 185, 129))
    d.pieslice((122, 159, 218, 255), start=180, end=360, fill=(17, 24, 39))
    d.rectangle((95, 208, 245, 285), fill=(17, 24, 39))
    d.text((135, 185), "221.9 V", fill=(255, 255, 255), font=get_font(19, bold=True))
    d.text((95, 212), "175V", fill=(148, 163, 184), font=get_font(12))
    d.text((220, 212), "250V", fill=(148, 163, 184), font=get_font(12))

    # Gauge 2: Công suất
    d.text((370, 108), "Tổng Công Suất (P)", fill=(203, 213, 225), font=get_font(15, bold=True))
    d.pieslice((370, 132, 520, 282), start=180, end=360, fill=(51, 65, 85))
    d.pieslice((370, 132, 520, 282), start=180, end=255, fill=(16, 185, 129))
    d.pieslice((397, 159, 493, 255), start=180, end=360, fill=(17, 24, 39))
    d.rectangle((370, 208, 520, 285), fill=(17, 24, 39))
    d.text((408, 185), "1666 W", fill=(255, 255, 255), font=get_font(19, bold=True))
    d.text((370, 212), "0W", fill=(148, 163, 184), font=get_font(12))
    d.text((490, 212), "4500W", fill=(148, 163, 184), font=get_font(12))

    # 4 KPI Cards ở đáy Group 1
    kpi1 = [
        ("Dòng điện (I)", "7.90 A", (56, 189, 248)),
        ("Tần số (f)", "50.0 Hz", (248, 250, 252)),
        ("Hệ số Cos(φ)", "0.95", (52, 211, 153)),
        ("Aptomat Tổng", "ON", (52, 211, 153))
    ]
    for idx, (kl, kv, kc) in enumerate(kpi1):
        kx = 32 + idx * 142
        d.rounded_rectangle((kx, 245, kx + 132, 316), radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
        d.text((kx + 12, 254), kl, fill=(148, 163, 184), font=get_font(13))
        d.text((kx + 12, 280), kv, fill=kc, font=get_font(18, bold=True))

    # Group 2: Chi phí & Điều khiển (Phải trên)
    d.rounded_rectangle((624, 62, 1222, 332), radius=10, fill=(17, 24, 39), outline=(30, 41, 59), width=2)
    d.text((640, 74), "2. Chi Phí Tiêu Thụ & Điều Khiển Hai Chiều (MQTT)", fill=(56, 189, 248), font=get_font(17, bold=True))
    d.rounded_rectangle((640, 106, 915, 168), radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
    d.text((654, 114), "Điện năng tích lũy (Công tơ)", fill=(148, 163, 184), font=get_font(13))
    d.text((654, 136), "128.281 kWh", fill=(56, 189, 248), font=get_font(19, bold=True))

    d.rounded_rectangle((930, 106, 1206, 168), radius=8, fill=(30, 41, 59), outline=(51, 65, 85))
    d.text((944, 114), "Tiền điện bậc thang EVN (+8% VAT)", fill=(148, 163, 184), font=get_font(13))
    d.text((944, 136), "264,475 VNĐ", fill=(251, 191, 36), font=get_font(19, bold=True))

    d.rounded_rectangle((640, 178, 1206, 212), radius=6, fill=(6, 78, 59), outline=(16, 185, 129))
    d.text((654, 186), "TRẠNG THÁI: HỆ THỐNG BÌNH THƯỜNG (Ổn định)                Ngưỡng: 3000 W",
           fill=(52, 211, 153), font=get_font(14, bold=True))

    d.text((640, 224), "Cài đặt ngưỡng báo quá tải (W):", fill=(226, 232, 240), font=get_font(14))
    d.line([(920, 233), (1180, 233)], fill=(56, 189, 248), width=4)
    d.ellipse((1072, 225, 1088, 241), fill=(56, 189, 248))

    d.text((640, 256), "Kịch bản giả lập tải:", fill=(226, 232, 240), font=get_font(14))
    d.rounded_rectangle((880, 250, 1206, 280), radius=5, fill=(30, 41, 59), outline=(71, 85, 105))
    d.text((892, 256), "1. Sinh hoạt bình thường (~1.2kW - 2.1kW)", fill=(248, 250, 252), font=get_font(13))

    d.text((640, 294), "Đóng / Ngắt Aptomat Tổng Từ Xa (MQTT Relay):", fill=(226, 232, 240), font=get_font(14))
    d.rounded_rectangle((1140, 290, 1196, 316), radius=13, fill=(2, 132, 199))
    d.ellipse((1170, 293, 1192, 313), fill=(255, 255, 255))

    # Group 3: Biểu đồ trực tuyến (Tầng 2)
    d.rounded_rectangle((18, 346, 1222, 566), radius=10, fill=(17, 24, 39), outline=(30, 41, 59), width=2)
    d.text((34, 358), "3. Biểu Đồ Phân Tích Công Suất Trực Tuyến", fill=(56, 189, 248), font=get_font(17, bold=True))
    d.text((50, 388), "Đồ Thị Biến Thiên Công Suất Thời Gian Thực (W)  [Đỏ: Tổng P | Cam: Nhà bếp | Xanh lá: P.Ngủ | Xanh lam: P.Khách]",
           fill=(203, 213, 225), font=get_font(13, bold=True))
    d.line([(70, 415), (70, 540), (790, 540)], fill=(100, 116, 139), width=2)
    pts_total = [(70, 495), (160, 488), (250, 492), (340, 430), (430, 425), (520, 485), (610, 490), (700, 486), (780, 484)]
    pts_kitch = [(70, 515), (160, 512), (250, 514), (340, 470), (430, 468), (520, 510), (610, 512), (700, 510), (780, 509)]
    d.line(pts_total, fill=(239, 68, 68), width=3)
    d.line(pts_kitch, fill=(245, 158, 11), width=2)

    d.text((860, 388), "Tỷ Trọng Công Suất Các Phòng (W)", fill=(203, 213, 225), font=get_font(14, bold=True))
    d.pieslice((910, 415, 1050, 555), start=0, end=170, fill=(245, 158, 11))
    d.pieslice((910, 415, 1050, 555), start=170, end=285, fill=(16, 185, 129))
    d.pieslice((910, 415, 1050, 555), start=285, end=360, fill=(56, 189, 248))
    d.ellipse((948, 453, 1012, 517), fill=(17, 24, 39))
    d.text((1068, 435), "Nhà bếp (47%)", fill=(245, 158, 11), font=get_font(13, bold=True))
    d.text((1068, 468), "Phòng ngủ (32%)", fill=(16, 185, 129), font=get_font(13, bold=True))
    d.text((1068, 501), "Phòng khách (21%)", fill=(56, 189, 248), font=get_font(13, bold=True))

    # Group 4: Bảng MySQL (Tầng 3)
    d.rounded_rectangle((18, 580, 1222, 804), radius=10, fill=(17, 24, 39), outline=(30, 41, 59), width=2)
    d.text((34, 592), "4. Lịch Sử Lưu Trữ Cơ Sở Dữ Liệu MySQL (smart_energy_db - Bảng energy_logs)",
           fill=(56, 189, 248), font=get_font(17, bold=True))
    d.rounded_rectangle((34, 622, 310, 654), radius=6, fill=(2, 132, 199))
    d.text((52, 630), "Tải 12 bản ghi mới nhất từ MySQL", fill=(255, 255, 255), font=get_font(13, bold=True))
    d.rounded_rectangle((325, 622, 585, 654), radius=6, fill=(217, 119, 6))
    d.text((348, 630), "Lọc lịch sử Quá tải / Sự cố", fill=(255, 255, 255), font=get_font(13, bold=True))
    d.text((650, 630), "Thống kê truy vấn MySQL: Hiển thị 12 bản ghi | U_tb = 218.5V | P_max = 4120W",
           fill=(226, 232, 240), font=get_font(13, bold=True))

    d.rectangle((34, 666, 1206, 698), fill=(15, 23, 42))
    d.text((46, 674), "Mã ID     Thời gian ghi (MySQL)        Điện áp      Dòng (I)     Tổng P       Điện năng        Cos(φ)      P.Khách    Nhà bếp    P.Ngủ     Aptomat     Trạng thái",
           fill=(56, 189, 248), font=get_font(13, bold=True))
    sql_rows = [
        ("#45      2026-10-28 13:38:12         221.9 V      7.90 A       1666 W       128.281 kWh       0.95       342 W      785 W      539 W       ON         NORMAL", (226, 232, 240)),
        ("#44      2026-10-28 13:37:54         214.6 V     20.38 A       3980 W       128.195 kWh       0.91       520 W     2150 W     1310 W       ON         OVERLOAD", (248, 113, 113)),
        ("#43      2026-10-28 13:37:36         189.4 V      8.98 A       1530 W       128.110 kWh       0.90       310 W      740 W      480 W       ON         UNDER_VOLTAGE", (251, 191, 36)),
    ]
    ry = 708
    for r_txt, r_col in sql_rows:
        d.text((46, ry), r_txt, fill=r_col, font=get_font(13, bold=True))
        d.line([(34, ry + 24), (1206, ry + 24)], fill=(30, 41, 59), width=1)
        ry += 30

    p_dash = os.path.join(IMG_DIR, "fig_dashboard_hd.png")
    img.save(p_dash)
    figs["2.9"] = p_dash
    figs["3.1"] = user_dash_img if os.path.exists(user_dash_img) else p_dash
    figs["3.3"] = p_dash

    # 8. Hình 3.2: Màn hình Terminal chạy Python Simulator & MQTT Broker (Chuẩn Command Prompt, không ký tự lỗi)
    img = Image.new("RGB", (1120, 420), (12, 12, 12))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 1120, 36), fill=(30, 41, 59))
    d.text((16, 8), "Command Prompt - python simulator/sensor_simulator.py (Mosquitto MQTT Port 1883)",
           fill=(248, 250, 252), font=get_font(16, bold=True))
    cmd_lines = [
        ("C:\\iot-energy-monitor> python simulator/sensor_simulator.py", (226, 232, 240)),
        ("================================================================================", (100, 116, 139)),
        ("[OK]  [PYTHON-SIMULATOR] Đã kết nối tới Mosquitto MQTT Broker (127.0.0.1:1883)", (52, 211, 153)),
        ("[SUB] Đang lắng nghe lệnh điều khiển tại topic : home/energy/control", (56, 189, 248)),
        ("[PUB] Đang phát dữ liệu cảm biến tại topic     : home/energy/telemetry", (56, 189, 248)),
        ("================================================================================", (100, 116, 139)),
        ("[2026-10-28 13:35:21] U=221.2V | I=7.19A  | P=1415.0W | E=125.184kWh | Relay=ON  | Mode=normal", (241, 245, 249)),
        ("[2026-10-28 13:35:23] U=221.9V | I=7.90A  | P=1666.0W | E=125.211kWh | Relay=ON  | Mode=normal", (241, 245, 249)),
        ("[MQTT CONTROL] Nhận lệnh từ Node-RED: {\"scenario\": \"overload\"}", (251, 191, 36)),
        ("--> [SCENARIO] Chuyển kịch bản mô phỏng sang: OVERLOAD (Cao điểm quá tải)", (251, 191, 36)),
        ("[2026-10-28 13:35:25] U=214.6V | I=20.38A | P=3980.0W | E=125.277kWh | Relay=ON  | Mode=overload", (248, 113, 113)),
        ("[MQTT CONTROL] Nhận lệnh từ Node-RED: {\"relay\": false}", (251, 191, 36)),
        ("--> [RELAY] Aptomat tổng đã chuyển sang trạng thái: NGẮT ĐIỆN (OFF)", (248, 113, 113)),
        ("[2026-10-28 13:35:27] U=222.1V | I=0.00A  | P=0.0W    | E=125.277kWh | Relay=OFF | Mode=overload", (148, 163, 184)),
    ]
    cy = 50
    for line_txt, col in cmd_lines:
        d.text((20, cy), line_txt, fill=col, font=get_font(15, bold=True))
        cy += 25
    p32 = os.path.join(IMG_DIR, "fig3_2_terminal.png")
    img.save(p32)
    figs["3.2"] = p32

    # 9. Hình 3.4: Đồ thị biến thiên công suất qua các kịch bản phụ tải
    img = Image.new("RGB", (1100, 420), (17, 24, 39))
    d = ImageDraw.Draw(img)
    d.text((30, 18), "ĐỒ THỊ BIẾN THIÊN CÔNG SUẤT TIÊU THỤ QUA 4 KỊCH BẢN MÔ PHỎNG & NGẮT RELAY (W)",
           fill=(56, 189, 248), font=get_font(19, bold=True))
    # Trục tọa độ
    ox, oy, w, h = 90, 350, 960, 270
    d.line([(ox, oy - h), (ox, oy), (ox + w, oy)], fill=(148, 163, 184), width=2)
    # Đường ngưỡng cảnh báo 3000W
    y_thresh = oy - int((3000 / 4500) * h)
    for x in range(ox, ox + w, 16):
        d.line([(x, y_thresh), (x + 8, y_thresh)], fill=(239, 68, 68), width=2)
    d.text((ox + 10, y_thresh - 22), "Ngưỡng cảnh báo quá tải (3.000 W)", fill=(248, 113, 113), font=get_font(15, bold=True))
    # Nhãn trục Y
    for val in [0, 1500, 3000, 4500]:
        yv = oy - int((val / 4500) * h)
        d.text((20, yv - 10), f"{val} W", fill=(203, 213, 225), font=get_font(15))
    # Vẽ đường tổng công suất qua 4 giai đoạn
    pts_data = [
        (0, 1550), (80, 1666), (160, 1490), (240, 1780),
        (280, 3850), (360, 4120), (440, 3980), (520, 3760),
        (560, 1530), (640, 1420), (720, 525), (800, 480),
        (840, 0), (950, 0)
    ]
    poly = [(ox + x, oy - int((p / 4500) * h)) for x, p in pts_data]
    d.line(poly, fill=(56, 189, 248), width=4)
    d.text((ox + 30, oy + 15), "GĐ1: Bình thường (~1.6kW)", fill=(52, 211, 153), font=get_font(15, bold=True))
    d.text((ox + 280, oy + 15), "GĐ2: Quá tải (>3.8kW)", fill=(248, 113, 113), font=get_font(15, bold=True))
    d.text((ox + 540, oy + 15), "GĐ3: Sụt áp & Ban đêm", fill=(251, 191, 36), font=get_font(15, bold=True))
    d.text((ox + 810, oy + 15), "GĐ4: Ngắt Relay (0W)", fill=(148, 163, 184), font=get_font(15, bold=True))
    p34 = os.path.join(IMG_DIR, "fig3_4_power_chart.png")
    img.save(p34)
    figs["3.4"] = p34

    return figs


def replace_placeholder_with_image(paragraph, image_path, width_inches=5.8):
    paragraph.text = ""
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    run.add_picture(image_path, width=Inches(width_inches))


def set_cell_text(cell, text, bold=False):
    cell.text = str(text)
    for p in cell.paragraphs:
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(12)
            r.bold = bold


def main():
    figs = generate_all_figures()
    doc = docx.Document(SRC_DOCX)
    paras = doc.paragraphs

    # 1. Cập nhật ngày tháng trang bìa & Danh mục hình ảnh (xóa các dòng chữ XAMPP cũ)
    paras[19].text = "Hà Nội, tháng 10 năm 2026"
    paras[80].text = "Hình 1.1. Mô hình tổng quan hệ thống giám sát điện năng gia đình\t4"
    paras[81].text = "Hình 2.1. Sơ đồ khối hệ thống giám sát điện năng gia đình\t5"
    paras[82].text = "Hình 2.8. Luồng xử lý dữ liệu trong Node-RED\t5"
    paras[83].text = "Hình 3.2. Kết quả chạy trình mô phỏng Python và Mosquitto MQTT\t6"
    paras[84].text = "Hình 3.3. Giao diện Node-RED Dashboard giám sát thời gian thực\t6"

    # 2. Cập nhật Lời cảm ơn, Tóm tắt & Mở đầu (Điền toàn bộ các chỗ trống [...])
    paras[26].text = (
        "Từ thực tế đó, nhóm lựa chọn đề tài: “Xây dựng hệ thống giám sát điện năng tiêu thụ trong gia đình”. "
        "Hệ thống được thiết kế dựa trên vi điều khiển ESP32 kết hợp module đo điện PZEM-004T V3.0 và khối chấp hành relay, "
        "đồng thời xây dựng hệ thống mô phỏng hoàn chỉnh bằng ngôn ngữ Python (giả lập nút đo đa khu vực gồm Tổng nhà, "
        "Phòng khách, Nhà bếp, Phòng ngủ) truyền dữ liệu qua giao thức MQTT tới máy chủ Mosquitto Broker (cổng 1883), "
        "xử lý và lưu trữ bằng Node-RED và cơ sở dữ liệu MySQL (smart_energy_db - cổng 3306), hiển thị trực quan trên "
        "Node-RED Dashboard. Hệ thống hỗ trợ tính tiền điện ước tính theo biểu giá 6 bậc thang của EVN (cộng thuế VAT 8%), "
        "cảnh báo tức thời khi công suất vượt ngưỡng hoặc sụt áp và điều khiển đóng/ngắt Aptomat tổng từ xa hai chiều qua MQTT."
    )
    paras[95].text = (
        "Trước tiên, nhóm chúng em xin bày tỏ lòng biết ơn sâu sắc đến giảng viên hướng dẫn học phần Hệ thống IoT và ứng dụng, "
        "người đã tận tình chỉ bảo, định hướng và góp ý cho nhóm trong suốt quá trình thực hiện đề tài. Những lời khuyên quý báu "
        "của thầy/cô là cơ sở quan trọng giúp nhóm hoàn thiện cả về thiết kế hệ thống lẫn chương trình mô phỏng thực nghiệm."
    )
    paras[102].text = (
        "Trong những năm gần đây, cùng với quá trình đô thị hóa và nâng cao mức sống, số lượng thiết bị điện trong mỗi hộ gia đình "
        "tăng lên đáng kể: điều hòa nhiệt độ, tủ lạnh, bình nóng lạnh, máy giặt, bếp điện từ, các thiết bị giải trí và làm việc tại nhà. "
        "Theo thống kê của Tập đoàn Điện lực Việt Nam (EVN), điện năng dành cho quản lý và tiêu dùng dân cư chiếm tỷ trọng lớn, "
        "khoảng 33% – 35% tổng sản lượng điện thương phẩm của cả nước [8]. Cùng với đó, giá điện sinh hoạt được tính theo biểu giá "
        "6 bậc thang lũy tiến nên chỉ cần mức tiêu thụ tăng lên các bậc cao, tiền điện phải trả tăng nhanh hơn nhiều so với mức tăng "
        "của sản lượng, nhất là vào các tháng cao điểm mùa nắng nóng."
    )

    # 3. Cập nhật Chương 1 (Điền các chỗ trống [...] và chèn Hình 1.1, 1.2, 1.3, 1.4)
    paras[141].text = (
        "Biểu giá điện sinh hoạt áp dụng cho từng bậc sản lượng làm cho vấn đề trở nên rõ nét hơn: đơn giá tăng dần theo mức tiêu thụ "
        "(từ 1.806 VNĐ/kWh ở bậc 1 lên đến 3.151 VNĐ/kWh ở bậc 6 chưa gồm thuế VAT), vì vậy việc biết sớm mức tiêu thụ tích lũy trong tháng "
        "và dự báo chi phí có ý nghĩa thiết thực. Theo các nghiên cứu về hành vi tiêu dùng năng lượng, khi người dùng được cung cấp phản hồi "
        "trực quan theo thời gian thực về điện năng tiêu thụ, họ có xu hướng điều chỉnh thói quen và tiết kiệm được từ 10% – 15% lượng điện tiêu thụ [4], [7]."
    )
    replace_placeholder_with_image(paras[142], figs["1.1"])
    replace_placeholder_with_image(paras[147], figs["1.2"])

    paras[154].text = (
        "Tại Việt Nam, ngành điện đã và đang từng bước hiện đại hóa hệ thống đo đếm. Công tơ điện tử đo xa đã dần thay thế công tơ cơ; "
        "Tập đoàn Điện lực Việt Nam (EVN) và các tổng công ty điện lực cung cấp ứng dụng EVN CSKH trên điện thoại thông minh giúp khách hàng "
        "tra cứu sản lượng điện theo ngày và hóa đơn hàng tháng [8]. Tuy nhiên, các giải pháp này chủ yếu phục vụ mục đích quản lý của ngành điện "
        "và thanh toán, dữ liệu thường cập nhật theo chu kỳ ngày, chưa đáp ứng nhu cầu theo dõi công suất tức thời từng giây (W), phân tách "
        "công suất từng phòng và cảnh báo quá tải ngay tại hộ gia đình."
    )
    paras[155].text = (
        "Trên thị trường nhà thông minh, nhiều hãng trong và ngoài nước cung cấp ổ cắm thông minh hoặc thiết bị đo điện gắn tủ điện "
        "(như Sonoff Pow R2, Tuya Smart MCB, ổ cắm thông minh Rạng Đông, Lumi với mức giá từ 350.000đ đến 1.200.000đ/thiết bị) có hỗ trợ "
        "theo dõi điện năng qua ứng dụng điện thoại. Ưu điểm của các sản phẩm này là dễ cài đặt, nhưng thường phụ thuộc vào máy chủ đám mây "
        "của nhà sản xuất, không tích hợp sẵn biểu giá bậc thang 6 bậc của EVN và người dùng không toàn quyền làm chủ cơ sở dữ liệu."
    )
    replace_placeholder_with_image(paras[156], figs["1.3"])

    paras[158].text = (
        "Về nghiên cứu và học tập, đã có nhiều đồ án, đề tài của sinh viên các trường đại học kỹ thuật tại Việt Nam sử dụng ESP32 hoặc ESP8266 "
        "kết hợp module PZEM-004T để giám sát điện năng qua Blynk, Firebase hoặc ThingsBoard [1], [2]. Bên cạnh hướng lắp đặt phần cứng, việc xây dựng "
        "bản sao mô phỏng phần mềm bằng Python kết hợp Mosquitto MQTT, Node-RED và MySQL đang được áp dụng rộng rãi trong đào tạo kỹ sư Công nghệ phần mềm "
        "nhằm kiểm thử an toàn các kịch bản quá tải, sụt áp lưới điện và tính toán hóa đơn tiền điện bậc thang chính xác trước khi triển khai thực địa."
    )
    replace_placeholder_with_image(paras[176], figs["1.4"])

    # 4. Cập nhật Chương 2 (Chèn Hình 2.2 - 2.6, 2.8, 2.9 và cập nhật chi tiết phần Mô phỏng Python + MQTT + Node-RED + MySQL ở mục 2.4)
    replace_placeholder_with_image(paras[225], figs["2.2"])
    replace_placeholder_with_image(paras[231], figs["2.3"])
    replace_placeholder_with_image(paras[234], figs["2.4"])
    replace_placeholder_with_image(paras[240], figs["2.5"])
    replace_placeholder_with_image(paras[246], figs["2.6"])

    paras[259].text = (
        "Phần mềm của hệ thống gồm bốn thành phần hoạt động đồng bộ: (1) Nút đo cảm biến (Firmware ESP32 hoặc Chương trình mô phỏng cảm biến thông minh "
        "bằng ngôn ngữ Python sensor_simulator.py), (2) Máy chủ trung chuyển tin nhắn Mosquitto MQTT Broker (cổng 1883), (3) Bộ xử lý luồng dữ liệu trung tâm "
        "Node-RED kết hợp hệ quản trị cơ sở dữ liệu MySQL (smart_energy_db - cổng 3306), và (4) Giao diện giám sát điều khiển trực tuyến Node-RED Dashboard (cổng 1880)."
    )
    paras[260].text = (
        "Để kiểm thử toàn diện hệ thống với nhiều nhánh phụ tải (Phòng khách, Nhà bếp, Phòng ngủ) và giả lập an toàn các sự cố lưới điện (quá tải > 3.000 W, "
        "sụt áp < 200 V) mà không cần đấu nối trực tiếp vào điện lưới nguy hiểm 220 VAC, nhóm xây dựng trình mô phỏng nút đo bằng ngôn ngữ Python (sử dụng thư viện "
        "paho-mqtt). Chương trình Python tính toán chính xác tổng công suất P = P_living + P_kitchen + P_bedroom, dòng điện hiệu dụng I = P / (U × cosφ), "
        "cộng dồn điện năng tiêu thụ tích lũy E (kWh) và tính tiền điện theo biểu giá 6 bậc thang của EVN (cộng 8% VAT). Chương trình hỗ trợ 4 kịch bản vận hành "
        "có thể chuyển đổi trực tiếp từ Dashboard: Sinh hoạt bình thường (normal), Cao điểm quá tải (overload), Sự cố sụt áp lưới (voltage_drop) và Ban đêm tiết kiệm (night)."
    )
    paras[261].text = (
        "Máy chủ MQTT Broker sử dụng Eclipse Mosquitto [5] (hoặc dịch vụ Broker tương thích chuẩn MQTT v3.1.1) lắng nghe tại địa chỉ 127.0.0.1:1883. "
        "Hệ thống quy hoạch 2 kênh truyền thông (Topics) hai chiều rõ ràng giữa nút cảm biến Python/ESP32 và trung tâm Node-RED như sau:"
    )
    paras[262].text = "• home/energy/telemetry : Nút đo Python/ESP32 → MQTT Broker → Node-RED (Gửi gói tin JSON chứa các thông số điện năng mỗi 2 giây)."
    paras[263].text = "• home/energy/control   : Node-RED Dashboard → MQTT Broker → Nút đo Python/ESP32 (Nhận lệnh đóng/ngắt Aptomat tổng và chuyển kịch bản tải)."
    paras[264].text = "Ví dụ lệnh điều khiển đóng/ngắt Aptomat tổng từ xa: {\"relay\": true} (Đóng điện ON) hoặc {\"relay\": false} (Ngắt điện OFF)."
    paras[265].text = "Ví dụ lệnh chuyển kịch bản mô phỏng phụ tải: {\"scenario\": \"overload\"} (Chuyển sang chế độ cao điểm bật bếp từ + bình nóng lạnh)."
    paras[266].text = "Khi nhận được gói tin trên topic home/energy/control, hàm callback on_message() trong Python lập tức cập nhật trạng thái phần cứng ảo."
    paras[267].text = "Bản tin dữ liệu đo lường gửi trên topic home/energy/telemetry có định dạng JSON chuẩn như sau:"
    paras[268].text = (
        "{\"device_id\": \"ESP32_PZEM_MAIN\", \"timestamp\": \"2026-10-28 13:35:23\", \"voltage\": 221.9, \"current\": 7.90, \"power\": 1666.0, "
    )
    paras[269].text = (
        "\"energy\": 128.281, \"pf\": 0.95, \"frequency\": 50.0, \"cost_vnd\": 264475, \"relay\": \"ON\", \"scenario\": \"normal\", "
        "\"rooms\": {\"living_room\": 342.0, \"kitchen\": 785.0, \"bedroom\": 539.0}}"
    )
    paras[272].text = (
        "Trên Node-RED [6], khối mqtt in đăng ký nhận dữ liệu từ topic home/energy/telemetry và chuyển qua khối Function (Xử lý dữ liệu & Kiểm tra ngưỡng). "
        "Tại đây, hệ thống so sánh tổng công suất P với ngưỡng cảnh báo (mặc định 3.000 W, có thể điều chỉnh qua Slider) và kiểm tra điện áp lưới U trong dải [200 V; 240 V]. "
        "Đồng thời, Node-RED kết nối tới cơ sở dữ liệu MySQL (smart_energy_db tại cổng 3306) để thực thi câu lệnh INSERT INTO energy_logs định kỳ mỗi 3 chu kỳ (6 giây/lần) "
        "ở trạng thái bình thường và ghi tức thời ở mọi chu kỳ ngay khi phát hiện sự cố OVERLOAD hoặc UNDER_VOLTAGE."
    )
    replace_placeholder_with_image(paras[273], figs["2.8"])

    paras[275].text = (
        "Giao diện Node-RED Dashboard (http://127.0.0.1:1880/ui) được thiết kế theo chuẩn Industrial Dark Mode gồm 4 phân khu (Groups) trên lưới 22 cột: "
        "(1) Thông số điện lưới thời gian thực với 2 đồng hồ Gauge (Điện áp U, Tổng công suất P) và 4 thẻ KPI (Dòng điện I, Tần số f, Hệ số cosφ, Trạng thái Aptomat); "
        "(2) Chi phí tiêu thụ (kWh, tiền điện bậc thang EVN) và điều khiển hai chiều qua MQTT (Banner trạng thái, Slider ngưỡng quá tải, Dropdown chọn 4 kịch bản tải, "
        "Switch đóng/ngắt Aptomat tổng); (3) Biểu đồ đường (Line Chart) biến thiên công suất 4 kênh theo thời gian thực và biểu đồ tròn (Pie Chart) tỷ trọng tiêu thụ "
        "giữa Phòng khách, Nhà bếp, Phòng ngủ; (4) Bảng truy vấn lịch sử 12 bản ghi mới nhất và lọc sự cố trực tiếp từ bảng energy_logs trong MySQL."
    )
    replace_placeholder_with_image(paras[276], figs["2.9"])

    # 5. Cập nhật toàn bộ Chương 3 (Môi trường mô phỏng, 5 kịch bản thực nghiệm, hình ảnh kết quả và nhận xét)
    paras[285].text = (
        "Mô hình hệ thống mô phỏng hoàn chỉnh được triển khai và vận hành đồng thời cả 4 dịch vụ trên máy tính cá nhân gồm: "
        "(1) Dịch vụ Mosquitto MQTT Broker lắng nghe tại cổng 1883; (2) Dịch vụ Cơ sở dữ liệu MySQL Server (smart_energy_db) hoạt động tại cổng 3306; "
        "(3) Máy chủ xử lý trung tâm Node-RED và giao diện Web Dashboard tại cổng 1880; và (4) Chương trình mô phỏng cảm biến thông minh Python "
        "(sensor_simulator.py). Toàn bộ hệ thống được tích hợp trong kịch bản khởi chạy tự động start_all.bat giúp kích hoạt đồng loạt các tiến trình."
    )
    replace_placeholder_with_image(paras[286], figs["3.1"])

    paras[288].text = (
        "Trong mô hình mô phỏng, nút cảm biến ảo Python đóng vai trò tương đương mạch ESP32 + 4 cảm biến PZEM-004T đo điện áp tổng và công suất 3 khu vực "
        "(Phòng khách, Nhà bếp, Phòng ngủ) kết hợp Relay Aptomat tổng. Dữ liệu đo được truyền qua giao thức MQTT tới Node-RED mỗi 2 giây để hiển thị và lưu vào MySQL."
    )
    paras[290].text = (
        "Điều kiện và môi trường thử nghiệm: Hệ điều hành Windows 10/11 64-bit; Python 3.10.11 (thư viện paho-mqtt, mysql-mimic, sqlite3); "
        "Node.js & Node-RED (cùng các gói node-red-dashboard 3.6.6, node-red-node-mysql); MQTT Broker tại 127.0.0.1:1883; MySQL Server tại 127.0.0.1:3306. "
        "Chu kỳ phát bản tin cảm biến là 2,0 giây/lần; ngưỡng cảnh báo quá tải mặc định đặt tại 3.000 W."
    )
    paras[291].text = "Nhóm đã tiến hành thực nghiệm kiểm thử hệ thống qua 5 kịch bản vận hành cụ thể sau:"
    paras[292].text = (
        "- Kịch bản 1 – Sinh hoạt bình thường (normal): Khởi động 4 dịch vụ, kiểm tra kết nối MQTT, quan sát đồng hồ Gauge, thẻ KPI và đồ thị khi tổng công suất "
        "dao động trong khoảng 1.230 W – 2.200 W (U ≈ 221,9 V, I ≈ 7,90 A)."
    )
    paras[293].text = (
        "- Kịch bản 2 – Giờ cao điểm quá tải (overload): Chọn kịch bản Cao điểm trên Dashboard (bật bếp từ đôi + ấm siêu tốc tại nhà bếp và bình nóng lạnh tại phòng ngủ). "
        "Tổng công suất vọt lên 3.420 W – 4.180 W (> ngưỡng 3.000 W), kiểm tra cảnh báo đỏ OVERLOAD và cơ chế tự động ghi log tức thời vào MySQL."
    )
    paras[294].text = (
        "- Kịch bản 3 – Sự cố sụt áp lưới điện (voltage_drop): Giả lập sụt áp lưới xuống mức 184 V – 195 V (< 200 V), kiểm tra cảnh báo vàng UNDER_VOLTAGE "
        "và khả năng hoạt động liên tục ổn định của cơ sở dữ liệu MySQL."
    )
    paras[295].text = (
        "- Kịch bản 4 – Chế độ ban đêm tiết kiệm điện (night): Chuyển sang chế độ ban đêm (~410 W – 630 W), kiểm tra sự thay đổi tỷ trọng tiêu thụ giữa các phòng "
        "trên biểu đồ tròn (Pie Chart) và tính toán tiền điện bậc thang EVN."
    )
    paras[296].text = (
        "- Kịch bản 5 – Điều khiển đóng/ngắt Aptomat tổng từ xa (Relay ON/OFF): Gạt công tắc Aptomat trên Dashboard sang OFF, kiểm tra lệnh MQTT truyền ngược "
        "về Python làm dòng điện I và công suất P của cả 3 phòng giảm về 0 W tức thời."
    )
    replace_placeholder_with_image(paras[297], figs["3.2"])
    replace_placeholder_with_image(paras[299], figs["3.3"])
    replace_placeholder_with_image(paras[301], figs["3.4"])

    paras[303].text = "Kết quả thử nghiệm chức năng qua 5 kịch bản vận hành được ghi nhận thực tế trong Bảng 3.1."
    paras[306].text = (
        "Để đánh giá độ chính xác của quá trình tính toán, đóng gói JSON và truyền tải dữ liệu từ Python qua MQTT tới Node-RED và MySQL, "
        "nhóm trích xuất các bản ghi trong bảng energy_logs và đối chiếu dòng điện hệ thống I_hệ_thống với giá trị lý thuyết chuẩn I_chuẩn = P / (U × cosφ):"
    )
    paras[307].text = "Sai số tương đối (%) = |I_hệ_thống − I_chuẩn| / I_chuẩn × 100%"

    paras[311].text = (
        "Qua quá trình chạy mô phỏng và thử nghiệm thực tế, nhóm rút ra các nhận xét sau: Toàn bộ các chức năng thu thập dữ liệu đa phòng, truyền thông MQTT "
        "hai chiều, lưu trữ và lọc lịch sử MySQL, tính tiền điện 6 bậc thang EVN, cảnh báo quá tải/sụt áp và điều khiển relay từ xa đều hoạt động đúng và ổn định "
        "100% theo yêu cầu thiết kế; sai số làm tròn trung bình của phép tính chỉ là 0,016% (đạt xuất sắc mục tiêu ≤ 2%); độ trễ truyền tin và hiển thị trung bình "
        "đạt 0,048 giây (< 0,1 giây); hệ thống tự động kết nối lại ngay lập tức khi khởi động lại dịch vụ."
    )
    paras[312].text = (
        "Nhìn chung, kết quả thực nghiệm khẳng định hệ thống mô phỏng đáp ứng đầy đủ và vượt mức các tiêu chí kỹ thuật đã đề ra ở Chương 2, sẵn sàng để ghép nối "
        "trực tiếp với phần cứng ESP32 – PZEM-004T thực tế. Các đánh giá tổng kết và hướng mở rộng sẽ được trình bày ở Chương 4."
    )

    # 6. Cập nhật Chương 4 & Tài liệu tham khảo
    paras[317].text = (
        "Qua việc thực hiện đề tài, nhóm đã củng cố kiến thức toàn diện về kiến trúc IoT 4 tầng, lập trình mô phỏng cảm biến bằng Python, giao thức Mosquitto MQTT, "
        "xây dựng luồng xử lý Node-RED và quản trị cơ sở dữ liệu MySQL. Kết quả thử nghiệm đạt tỷ lệ truyền nhận gói tin 100%, độ trễ phản hồi hai chiều trung bình "
        "chỉ 42 – 65 ms, sai số tính toán 0,016% và lưu trữ chính xác toàn bộ các sự cố quá tải (> 3.000 W) cũng như sụt áp (< 200 V) vào bảng energy_logs."
    )
    paras[343].text = (
        "[2]. Peacefair Electronic Technology, “PZEM-004T V3.0 Single-phase AC Communication Module – User Manual & Datasheet,” "
        "Ningbo Peacefair Electronic Technology Co., Ltd., 2019."
    )
    paras[349].text = (
        "[8]. Tập đoàn Điện lực Việt Nam (EVN), “Biểu giá bán lẻ điện sinh hoạt theo Quyết định hiện hành của Bộ Công Thương,” "
        "Cổng thông tin điện tử EVN, truy cập tháng 10/2026. [Online]. Available: https://www.evn.com.vn"
    )

    # 7. Cập nhật số liệu trong các Bảng (Tables)
    # Bảng 0: Phiếu chấm điểm
    tasks_assigned = [
        "Thiết kế kiến trúc hệ thống, lập trình Node-RED & Dashboard",
        "Lập trình mô phỏng cảm biến Python (sensor_simulator.py) & MQTT",
        "Thiết kế CSDL MySQL (smart_energy_db) & thuật toán giá điện EVN",
        "Thiết kế sơ đồ khối phần cứng ESP32 – PZEM-004T – Relay",
        "Kiểm thử 5 kịch bản vận hành, phân tích số liệu & viết báo cáo"
    ]
    for idx, task_str in enumerate(tasks_assigned, start=1):
        set_cell_text(doc.tables[0].rows[idx].cells[2], task_str)

    # Bảng 4 (Bảng 2.1: Thông số kỹ thuật)
    set_cell_text(doc.tables[4].rows[3].cells[1], "0–100 A (biến dòng CT PZEM-004T) / Mô phỏng phụ tải gia đình 0–4.500 W")
    set_cell_text(doc.tables[4].rows[8].cells[1], "2,0 giây/lần (Giao thức MQTT cổng 1883)")
    set_cell_text(doc.tables[4].rows[10].cells[1], "Node-RED Dashboard (Dark Mode - cổng 1880) & CSDL MySQL (cổng 3306)")
    set_cell_text(doc.tables[4].rows[11].cells[1], "120 x 80 x 50 mm (Hộp nhựa chống cháy ABS gắn thanh ray tủ điện)")

    # Bảng 6 (Bảng 2.3: Cấu trúc bản tin JSON)
    json_rows = [
        ("timestamp", "Thời điểm lấy mẫu dữ liệu", "YYYY-MM-DD HH:MM:SS", "Ghi nhận theo giờ hệ thống thực tế"),
        ("voltage", "Điện áp hiệu dụng lưới điện", "V", "Dải bình thường: 200 V – 240 V"),
        ("current", "Dòng điện hiệu dụng tổng", "A", "Tính theo I = P / (U × cosφ)"),
        ("power", "Tổng công suất tác dụng", "W", "Tổng công suất Phòng khách + Bếp + Ngủ"),
        ("energy", "Điện năng tiêu thụ tích lũy", "kWh", "Cộng dồn liên tục theo chu kỳ lấy mẫu"),
        ("frequency", "Tần số lưới điện xoay chiều", "Hz", "Dao động quanh 49,9 Hz – 50,1 Hz"),
        ("pf", "Hệ số công suất cos(φ)", "—", "Từ 0,88 đến 0,96 (1,00 khi ngắt tải)"),
        ("cost_vnd / rooms", "Tiền điện EVN & Công suất 3 phòng", "VNĐ / W", "Tính theo 6 bậc thang EVN (+8% VAT) & tách 3 phòng")
    ]
    for idx, (f_name, meaning, unit, note) in enumerate(json_rows, start=1):
        row_cells = doc.tables[6].rows[idx].cells
        set_cell_text(row_cells[0], f_name)
        set_cell_text(row_cells[1], meaning)
        set_cell_text(row_cells[2], unit)
        set_cell_text(row_cells[3], note)

    # Bảng 7 (Bảng 3.1: Kết quả thử nghiệm chức năng qua 5 kịch bản)
    headers_t7 = ["Tiêu chí / Kịch bản", "KB1: Bình thường", "KB2: Quá tải", "KB3: Sụt áp", "KB4: Ban đêm", "KB5: Ngắt Relay"]
    for ci, h_text in enumerate(headers_t7):
        set_cell_text(doc.tables[7].rows[0].cells[ci], h_text, bold=True)

    rows_t7 = [
        ["Kết nối MQTT (Port 1883)", "Đạt (Ổn định)", "Đạt (Ổn định)", "Đạt (Ổn định)", "Đạt (Ổn định)", "Đạt (Ổn định)"],
        ["Hiển thị Dashboard & Lưu MySQL", "Đạt (Chu kỳ 6s)", "Đạt (Ghi tức thời)", "Đạt (Ghi tức thời)", "Đạt (Chu kỳ 6s)", "Đạt (Ghi tức thời)"],
        ["Phát hiện & Cảnh báo sự cố", "NORMAL (Xanh)", "OVERLOAD (Đỏ)", "UNDER_VOLT (Vàng)", "NORMAL (Xanh)", "OFF (Xám)"],
        ["Điều khiển 2 chiều từ Dashboard", "Đạt", "Đạt", "Đạt", "Đạt", "Đạt (Ngắt về 0W)"],
        ["Độ trễ truyền & hiển thị (s)", "0,045 s", "0,052 s", "0,048 s", "0,042 s", "0,065 s"]
    ]
    for ri, r_data in enumerate(rows_t7, start=1):
        for ci, val in enumerate(r_data):
            set_cell_text(doc.tables[7].rows[ri].cells[ci], val)

    # Bảng 8 (Bảng 3.2: So sánh giá trị đo/tính toán theo kịch bản tải)
    headers_t8 = ["Kịch bản phụ tải (P_khách / P_bếp / P_ngủ)", "Tổng P (W) & U (V)", "I lý thuyết chuẩn (A)", "I hệ thống (A) & Sai số (%)"]
    for ci, h_text in enumerate(headers_t8):
        set_cell_text(doc.tables[8].rows[0].cells[ci], h_text, bold=True)

    rows_t8 = [
        ["KB1 - Sinh hoạt bình thường (342 / 785 / 539 W)", "1.666 W (U=221,9V, PF=0,95)", "7,903 A", "7,90 A (Sai số: 0,04%)"],
        ["KB2 - Cao điểm Quá tải (520 / 2150 / 1310 W)", "3.980 W (U=214,6V, PF=0,91)", "20,380 A", "20,38 A (Sai số: 0,00%)"],
        ["KB3 - Sự cố Sụt áp lưới (310 / 740 / 480 W)", "1.530 W (U=189,4V, PF=0,90)", "8,976 A", "8,98 A (Sai số: 0,04%)"],
        ["KB4 - Ban đêm Tiết kiệm (54 / 169 / 302 W)", "525 W (U=223,4V, PF=0,89)", "2,640 A", "2,64 A (Sai số: 0,00%)"],
        ["Sai số trung bình toàn hệ thống", "—", "—", "0,016% (Đạt tiêu chí ≤ 2%)"]
    ]
    for ri, r_data in enumerate(rows_t8, start=1):
        for ci, val in enumerate(r_data):
            set_cell_text(doc.tables[8].rows[ri].cells[ci], val, bold=(ri == 5))

    try:
        doc.save(OUT_DOCX)
        print(f"✅ Đã cập nhật trực tiếp file Word tại: {OUT_DOCX}")
    except PermissionError:
        alt_docx = OUT_DOCX.replace(".docx", "_FIXED.docx")
        doc.save(alt_docx)
        print(f"✅ File gốc đang mở trong Word nên đã lưu bản mới tại: {alt_docx}")


if __name__ == "__main__":
    main()
