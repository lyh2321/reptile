import schedule
import time
import paramiko
import re


def sshd():
    ssh = paramiko.SSHClient()
    key = paramiko.AutoAddPolicy()
    ssh.set_missing_host_key_policy(key)
    ip = '127.0.0.1'
    ssh.connect(ip, 22, 'root', 'r2!Z]R=Q]Sc{udDg', timeout=10)
    print("Success : " + ip)

    global channel  # 全局变量
    channel = ssh.invoke_shell()
    channel.settimeout(10)

    pythonnamearray = ['proxy']

    stdin, stdout, stderr = ssh.exec_command('ps -ef|grep python')

    for pythonname in pythonnamearray:
        status = False
        for i in stdout.readlines():
            value = re.sub(' +', ' ', i)
            print(value)
            if i.find(pythonname) > -1:
                status = True
                break;

        if (status):
            chsend('nohup python3 ' + pythonname + '.py > ' + pythonname + '.log > 2>&1 & ')
            print(channel.recv(9999))
            chsend(' ')
            print(channel.recv(9999))
            chsend('exit')
            print(channel.recv(9999))

    channel.close()
    ssh.close()


def chsend(val):
    channel.send(val + '\n')
    time.sleep(3);


global channel

sshd()

# schedule.every().day.at("00:30").do(sshd)
# print('启动成功')
# while True:
#     schedule.run_pending()
#     time.sleep(1)
