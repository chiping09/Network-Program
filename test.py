import telnetlib

username="cisco"
password="cisco"
IP='172.18.7.87'

tn = telnetlib.Telnet(IP)

tn.read_until(b'Username: ')
tn.write(username.encode('ascii') + b'\n')

if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b'\n')

tn.write(b"conf t \n")
tn.write(b"int lo 10 \n")
tn.write(b"ip add 10.10.10.10 255.255.255.255 \n")
tn.write(b"end \n")
tn.write(b"exit \n")
print(tn.read_all().decode('ascii'))