"""
===============================================================================
CHƯƠNG TRÌNH MÔ PHỎNG CẢM BIẾN ĐO ĐIỆN NĂNG THÔNG MINH (ESP32 + PZEM-004T)
Giao thức: MQTT (Mosquitto Broker - Port 1883)
- Topic gửi dữ liệu (Publish):   home/energy/telemetry
- Topic nhận điều khiển (Sub):   home/energy/control
===============================================================================
"""

import json
import random
import sys
import time
from datetime import datetime
import paho.mqtt.client as mqtt

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Cấu hình kết nối Mosquitto MQTT Broker
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
TOPIC_TELEMETRY = "home/energy/telemetry"
TOPIC_CONTROL = "home/energy/control"
DEVICE_ID = "ESP32_PZEM_MAIN"

# Trạng thái mô phỏng của thiết bị IoT
state = {
    "relay_on": True,            # Trạng thái Aptomat tổng (True = ON, False = OFF)
    "scenario": "normal",        # normal | overload | voltage_drop | night
    "total_energy_kwh": 125.160, # Điện năng tích lũy đầu kỳ (kWh)
    "interval_sec": 2.0          # Chu kỳ gửi dữ liệu (2 giây/lần)
}


def calculate_evn_bill(kwh: float) -> int:
    """
    Tính tiền điện sinh hoạt theo biểu giá bậc thang 6 bậc của EVN (chưa gồm VAT 8%)
    và cộng thuế VAT 8%.
    """
    tiers = [
        (50, 1806),
        (50, 1866),
        (100, 2167),
        (100, 2729),
        (100, 3050),
        (float("inf"), 3151)
    ]
    remaining = kwh
    cost = 0.0
    for limit, price in tiers:
        if remaining <= 0:
            break
        used = min(remaining, limit)
        cost += used * price
        remaining -= used
    return int(round(cost * 1.08))  # Cộng 8% VAT


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("================================================================")
        print(f"✅ [PYTHON-SIMULATOR] Đã kết nối tới MQTT Broker ({MQTT_BROKER}:{MQTT_PORT})")
        client.subscribe(TOPIC_CONTROL)
        print(f"📡 Đang lắng nghe lệnh điều khiển tại topic: {TOPIC_CONTROL}")
        print(f"📤 Đang phát dữ liệu cảm biến tại topic:     {TOPIC_TELEMETRY}")
        print("================================================================")
    else:
        print(f"❌ [PYTHON-SIMULATOR] Kết nối MQTT thất bại, mã lỗi: {rc}")


def on_message(client, userdata, msg):
    """Xử lý lệnh điều khiển 2 chiều từ Node-RED Dashboard gửi xuống qua MQTT."""
    try:
        payload_str = msg.payload.decode("utf-8").strip()
        print(f"📥 [MQTT CONTROL] Nhận lệnh từ Node-RED: {payload_str}")

        # Hỗ trợ cả chuỗi đơn giản ("ON"/"OFF") hoặc JSON
        if payload_str.upper() in ("ON", "TRUE", "1"):
            state["relay_on"] = True
            return
        elif payload_str.upper() in ("OFF", "FALSE", "0"):
            state["relay_on"] = False
            return

        data = json.loads(payload_str)
        if "relay" in data:
            state["relay_on"] = bool(data["relay"])
            status_str = "ĐÓNG ĐIỆN (ON)" if state["relay_on"] else "NGẮT ĐIỆN (OFF)"
            print(f"🔌 [RELAY] Aptomat tổng đã chuyển sang trạng thái: {status_str}")

        if "scenario" in data:
            state["scenario"] = data["scenario"]
            print(f"🎭 [SCENARIO] Chuyển kịch bản mô phỏng sang: {state['scenario'].upper()}")

        if "reset_kwh" in data and data["reset_kwh"]:
            state["total_energy_kwh"] = 0.0
            print("🔄 [ENERGY] Đã reset chỉ số công tơ điện về 0.0 kWh")

    except Exception as e:
        print(f"⚠️ [PYTHON-SIMULATOR] Lỗi đọc gói tin điều khiển: {e}")


def generate_sensor_data() -> dict:
    """Sinh dữ liệu giả lập sát thực tế của cảm biến PZEM-004T theo kịch bản."""
    scenario = state["scenario"]

    # 1. Điện áp (V) & Tần số (Hz) & Hệ số công suất (PF)
    if scenario == "voltage_drop":
        voltage = round(random.uniform(184.0, 195.0), 1)
    elif scenario == "overload":
        voltage = round(random.uniform(212.0, 217.5), 1)
    else:
        voltage = round(random.uniform(219.0, 224.5), 1)

    frequency = round(random.uniform(49.9, 50.1), 1)
    pf = round(random.uniform(0.88, 0.96), 2)

    # 2. Công suất từng khu vực trong nhà (W)
    if not state["relay_on"]:
        # Khi Aptomat tổng OFF: không có dòng điện tiêu thụ
        p_living = 0.0
        p_kitchen = 0.0
        p_bedroom = 0.0
        pf = 1.00
    else:
        if scenario == "normal":
            p_living = round(random.uniform(280, 450), 0)    # TV + Đèn + Quạt
            p_kitchen = round(random.uniform(600, 1100), 0)  # Tủ lạnh + Nồi cơm
            p_bedroom = round(random.uniform(350, 650), 0)   # Điều hòa Inverter duy trì
        elif scenario == "overload":
            p_living = round(random.uniform(450, 600), 0)    # TV + Dàn âm thanh + Đèn
            p_kitchen = round(random.uniform(1800, 2300), 0) # Bếp từ công suất lớn + Ấm siêu tốc
            p_bedroom = round(random.uniform(1100, 1450), 0) # Bình nóng lạnh + Điều hòa
        elif scenario == "night":
            p_living = round(random.uniform(25, 60), 0)      # Router WiFi + Đèn hành lang
            p_kitchen = round(random.uniform(120, 180), 0)   # Tủ lạnh chạy chế độ nghỉ
            p_bedroom = round(random.uniform(250, 420), 0)   # Điều hòa chế độ Sleep
        else:  # voltage_drop
            p_living = round(random.uniform(260, 400), 0)
            p_kitchen = round(random.uniform(550, 900), 0)
            p_bedroom = round(random.uniform(350, 600), 0)

    total_power = round(p_living + p_kitchen + p_bedroom, 1)

    # 3. Tính dòng điện I = P / (U * cos(phi))
    if state["relay_on"] and voltage > 0 and pf > 0:
        current = round(total_power / (voltage * pf), 2)
    else:
        current = 0.0

    # 4. Cộng dồn điện năng tiêu thụ (kWh)
    # Trong mô phỏng, ta nhân hệ số gia tốc thời gian (x30) để thấy rõ số kWh và tiền điện tăng lên khi demo
    delta_kwh = (total_power / 1000.0) * (state["interval_sec"] / 3600.0) * 30.0
    state["total_energy_kwh"] = round(state["total_energy_kwh"] + delta_kwh, 4)

    cost_vnd = calculate_evn_bill(state["total_energy_kwh"])

    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "voltage": voltage,
        "current": current,
        "power": total_power,
        "energy": round(state["total_energy_kwh"], 3),
        "pf": pf,
        "frequency": frequency,
        "cost_vnd": cost_vnd,
        "relay": "ON" if state["relay_on"] else "OFF",
        "scenario": scenario,
        "rooms": {
            "living_room": p_living,
            "kitchen": p_kitchen,
            "bedroom": p_bedroom
        }
    }


def main():
    # Khởi tạo MQTT Client (Hỗ trợ paho-mqtt v1 và v2)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="Python_PZEM004T_Simulator")
    except AttributeError:
        client = mqtt.Client(client_id="Python_PZEM004T_Simulator")

    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            break
        except Exception as e:
            print(f"⏳ Đang chờ MQTT Broker tại {MQTT_BROKER}:{MQTT_PORT}... ({e})")
            time.sleep(2)

    client.loop_start()

    try:
        while True:
            payload = generate_sensor_data()
            json_str = json.dumps(payload, ensure_ascii=False)
            client.publish(TOPIC_TELEMETRY, json_str, qos=0)
            print(
                f"⚡ [{payload['timestamp']}] U={payload['voltage']}V | "
                f"I={payload['current']}A | P={payload['power']}W | "
                f"E={payload['energy']}kWh | Relay={payload['relay']} | Mode={payload['scenario']}"
            )
            time.sleep(state["interval_sec"])
    except KeyboardInterrupt:
        print("\n🛑 Đã dừng trình mô phỏng cảm biến Python.")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
