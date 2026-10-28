@echo off
chcp 65001 >nul
title He Thong Mo Phong IoT Giam Sat Dien Nang Gia Dinh
cd /d "%~dp0"

echo ============================================================================
echo   KHOI DONG HE THONG IOT GIAM SAT DIEN NANG GIA DINH
echo   (Python + Mosquitto MQTT + Node-RED + MySQL)
echo ============================================================================

echo [1/4] Khoi dong MQTT Broker (Port 1883)...
start "1. MQTT Broker (1883)" cmd /k "node services\mqtt_broker.js"
timeout /t 2 /nobreak >nul

echo [2/4] Khoi dong MySQL Server - smart_energy_db (Port 3306)...
start "2. MySQL Server (3306)" cmd /k "python services\mysql_server.py"
timeout /t 2 /nobreak >nul

echo [3/4] Khoi dong Node-RED & Dashboard (Port 1880)...
start "3. Node-RED Server (1880)" cmd /k "npx node-red -u .\nodered_data -s .\nodered_data\settings.js"
timeout /t 4 /nobreak >nul

echo [4/4] Khoi dong Python Virtual Sensor PZEM-004T...
start "4. Python Sensor Simulator" cmd /k "python simulator\sensor_simulator.py"

echo.
echo ============================================================================
echo   TAT CA DICH VU DA KHOI DONG THANH CONG!
echo   - Giao dien Node-RED Dashboard: http://127.0.0.1:1880/ui
echo   - So do khoi Node-RED Editor:   http://127.0.0.1:1880
echo ============================================================================
start http://127.0.0.1:1880/ui
pause
