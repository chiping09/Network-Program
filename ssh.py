from flask import Flask, render_template, request
from netmiko import ConnectHandler
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

# Route สำหรับหน้าตั้งค่าอุปกรณ์
@app.route('/config_device', methods=['GET', 'POST'])
def config_device():
    if request.method == 'POST':
        ip = request.form.get('ip')
        username = request.form.get('username')
        password = request.form.get('password')
        hostname = request.form.get('hostname')
        domain = request.form.get('domain')
        connection_type = request.form.get('connection_type')  # รับค่าสำหรับประเภทการเชื่อมต่อ

        # ตั้งค่าอุปกรณ์ผ่าน Netmiko หรือ Telnet
        if connection_type == 'ssh':
            result = setup_ssh(ip, username, password, hostname, domain)
        elif connection_type == 'telnet':
            result = setup_telnet(ip, username, password, hostname, domain)
        else:
            result = "Please select a valid connection type."

        return render_template('config_device.html', result=result)

    return render_template('config_device.html')

# ฟังก์ชันตั้งค่า SSH บนอุปกรณ์
def setup_ssh(ip, username, password, hostname, domain):
    device_info = {
        'device_type': 'cisco_ios',
        'ip': ip,
        'username': username,
        'password': password
    }
    config_commands = [
        f'hostname {hostname}',
        f'ip domain-name {domain}',
        'crypto key generate rsa modulus 2048',
        f'username {username} privilege 15 secret {password}',
        'line vty 0 4',
        'transport input ssh',
        'login local',
        'ip ssh version 2'
    ]

    try:
        connection = ConnectHandler(**device_info)
        output = connection.send_config_set(config_commands)
        connection.disconnect()
        return "การตั้งค่า SSH เสร็จสมบูรณ์:\n" + output
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

# ฟังก์ชันตั้งค่า Telnet บนอุปกรณ์
def setup_telnet(ip, username, password, hostname, domain):
    try:
        tn = telnetlib.Telnet(ip)

        # ล็อกอิน
        tn.read_until(b'Username: ')
        tn.write(username.encode('ascii') + b'\n')

        if password:
            tn.read_until(b"Password: ")
            tn.write(password.encode('ascii') + b'\n')

        # คำสั่งตั้งค่า
        tn.write(f"conf t\n".encode('ascii'))
        tn.write(f"hostname {hostname}\n".encode('ascii'))
        tn.write(f"ip domain-name {domain}\n".encode('ascii'))
        tn.write(f"username {username} privilege 15 secret {password}\n".encode('ascii'))
        tn.write(b"exit\n")
        tn.write(b"end\n")
        tn.write(b"exit\n")

        # อ่านผลลัพธ์ทั้งหมด
        output = tn.read_all().decode('ascii')
        return "การตั้งค่า Telnet เสร็จสมบูรณ์:\n" + output
    except Exception as e:
        return f"เกิดข้อผิดพลาด: {e}"

if __name__ == '__main__':
    app.run(debug=True)
