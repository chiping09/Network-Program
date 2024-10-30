from flask import Flask, render_template, request, jsonify
import telnetlib

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# หน้าเพื่อตั้งค่าอุปกรณ์
@app.route('/device_config')
def device_config():
    return render_template('device_config.html')

# หน้าอื่น ๆ
@app.route('/other_page')
def other_page():
    return render_template('other_page.html')

@app.route('/config_device', methods=['POST'])
def config_device():
    data = request.json
    ip = data['ip']
    username = data['username']
    password = data['password']
    interface = data['interface']
    ip_address = data['ipAddress']
    subnet_mask = data['subnetMask']
    status = data['status']  # รับค่าสถานะจาก dropdown

    commands = [
        'conf t',
        f'interface {interface}',  # ใช้ interface ที่เลือกจาก dropdown
        f'ip address {ip_address} {subnet_mask}',  # ใช้ IP และ subnet ที่ป้อน
        f'{"no shut" if status == "up" else "shutdown"}',  # คำสั่งเพื่อเปิดหรือปิด interface
        'exit',
        'end',
        'exit'
    ]

    try:
        tn = telnetlib.Telnet(ip)

        # ล็อกอิน
        tn.read_until(b'Username: ')
        tn.write(username.encode('ascii') + b'\n')

        if password:
            tn.read_until(b"Password: ")
            tn.write(password.encode('ascii') + b'\n')

        # ส่งคำสั่ง
        for command in commands:
            tn.write(command.encode('ascii') + b'\n')

        # อ่านผลลัพธ์ทั้งหมด
        output = tn.read_all().decode('ascii')
        return jsonify(success=True, output=output)
    except Exception as e:
        return jsonify(success=False, error=str(e))


if __name__ == '__main__':
    app.run(debug=True)
