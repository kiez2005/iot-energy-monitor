-- ============================================================================
-- ĐỀ TÀI: HỆ THỐNG IOT GIÁM SÁT ĐIỆN NĂNG TIÊU THỤ TRONG GIA ĐÌNH
-- Cơ sở dữ liệu: MySQL (smart_energy_db)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS smart_energy_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_energy_db;

-- 1. Bảng lưu trữ thông số điện năng định kỳ từ cảm biến PZEM-004T (qua MQTT -> Node-RED)
CREATE TABLE IF NOT EXISTS energy_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_id VARCHAR(50) NOT NULL DEFAULT 'ESP32_PZEM_MAIN',
    voltage FLOAT NOT NULL COMMENT 'Điện áp hiệu dụng (V)',
    current_amp FLOAT NOT NULL COMMENT 'Dòng điện hiệu dụng (A)',
    power_watt FLOAT NOT NULL COMMENT 'Tổng công suất tác dụng (W)',
    energy_kwh FLOAT NOT NULL COMMENT 'Điện năng tiêu thụ tích lũy (kWh)',
    power_factor FLOAT NOT NULL COMMENT 'Hệ số công suất cos(phi)',
    frequency FLOAT NOT NULL COMMENT 'Tần số lưới điện (Hz)',
    living_room_w FLOAT DEFAULT 0 COMMENT 'Công suất Phòng khách (W)',
    kitchen_w FLOAT DEFAULT 0 COMMENT 'Công suất Nhà bếp (W)',
    bedroom_w FLOAT DEFAULT 0 COMMENT 'Công suất Phòng ngủ (W)',
    relay_state VARCHAR(10) DEFAULT 'ON' COMMENT 'Trạng thái Aptomat (ON/OFF)',
    status_alert VARCHAR(50) DEFAULT 'NORMAL' COMMENT 'Trạng thái: NORMAL, OVERLOAD, OVER_VOLTAGE, UNDER_VOLTAGE'
);

-- 2. Bảng lưu lịch sử sự cố / cảnh báo quá tải
CREATE TABLE IF NOT EXISTS alert_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    alert_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    alert_type VARCHAR(50) NOT NULL,
    power_watt FLOAT NOT NULL,
    voltage FLOAT NOT NULL,
    message VARCHAR(255) NOT NULL
);

-- ============================================================================
-- CÁC CÂU TRUY VẤN MẪU DÙNG TRONG NODE-RED VÀ BÁO CÁO ĐỒ ÁN
-- ============================================================================

-- Truy vấn 15 bản ghi mới nhất hiển thị lên Dashboard:
-- SELECT id, DATE_FORMAT(recorded_at, '%H:%i:%s %d/%m') AS time_str,
--        voltage, current_amp, power_watt, energy_kwh, power_factor,
--        living_room_w, kitchen_w, bedroom_w, status_alert
-- FROM energy_logs
-- ORDER BY id DESC LIMIT 15;

-- Thống kê công suất trung bình, lớn nhất và điện năng tiêu thụ trong ngày:
-- SELECT COUNT(*) AS total_samples,
--        ROUND(AVG(voltage), 1) AS avg_voltage,
--        ROUND(AVG(power_watt), 0) AS avg_power,
--        MAX(power_watt) AS peak_power,
--        ROUND(MAX(energy_kwh) - MIN(energy_kwh), 3) AS daily_kwh
-- FROM energy_logs
-- WHERE DATE(recorded_at) = CURDATE();
