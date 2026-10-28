/**
 * MQTT Broker Service (Port 1883)
 * - Tự động kiểm tra nếu máy đã cài Eclipse Mosquitto thì gọi mosquitto.exe với file mosquitto.conf.
 * - Nếu chưa cài đặt Mosquitto.exe ở quyền Admin, tự động khởi chạy MQTT Broker chuẩn (Aedes)
 *   ngay trên cổng 1883 với định dạng log giống hệt Mosquitto để Python & Node-RED kết nối trực tiếp!
 */

const net = require('net');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const PORT = 1883;
const HOST = '127.0.0.1';

const mosquittoPaths = [
    'C:\\Program Files\\mosquitto\\mosquitto.exe',
    'C:\\Program Files (x86)\\mosquitto\\mosquitto.exe'
];

function findMosquittoExe() {
    for (const p of mosquittoPaths) {
        if (fs.existsSync(p)) return p;
    }
    return null;
}

async function startEmbeddedBroker() {
    const { Aedes } = require('aedes');
    const aedes = await Aedes.createBroker();
    const server = net.createServer(aedes.handle);

    aedes.on('client', (client) => {
        console.log(`[MQTT-BROKER 1883] New client connected: ${client ? client.id : 'unknown'}`);
    });

    aedes.on('clientDisconnect', (client) => {
        console.log(`[MQTT-BROKER 1883] Client disconnected: ${client ? client.id : 'unknown'}`);
    });

    aedes.on('subscribe', (subscriptions, client) => {
        const topics = subscriptions.map(s => s.topic).join(', ');
        console.log(`[MQTT-BROKER 1883] Client ${client ? client.id : 'unknown'} subscribed to: ${topics}`);
    });

    aedes.on('publish', (packet, client) => {
        if (client && !packet.topic.startsWith('$SYS')) {
            const payloadStr = packet.payload.toString('utf8');
            const preview = payloadStr.length > 120 ? payloadStr.substring(0, 120) + '...' : payloadStr;
            console.log(`[MQTT-BROKER 1883] PUBLISH from ${client.id} -> Topic '${packet.topic}': ${preview}`);
        }
    });

    server.listen(PORT, HOST, () => {
        console.log(`================================================================`);
        console.log(`🚀 MQTT Broker (Mosquitto-compatible) đang chạy tại mqtt://${HOST}:${PORT}`);
        console.log(`================================================================`);
    });

    server.on('error', (err) => {
        if (err.code === 'EADDRINUSE') {
            console.log(`[MQTT-BROKER 1883] Cổng ${PORT} đã có MQTT Broker đang chạy sẵn.`);
            process.exit(0);
        } else {
            console.error(`[MQTT-BROKER 1883] Lỗi:`, err);
        }
    });
}

const mosqExe = findMosquittoExe();
const confPath = path.join(__dirname, '..', 'mosquitto', 'mosquitto.conf');

if (mosqExe && fs.existsSync(confPath)) {
    console.log(`[MQTT-BROKER] Khởi chạy Eclipse Mosquitto từ: ${mosqExe}`);
    const proc = spawn(mosqExe, ['-c', confPath, '-v'], { stdio: 'inherit' });
    proc.on('error', () => startEmbeddedBroker());
} else {
    startEmbeddedBroker();
}
