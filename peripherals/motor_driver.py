import paho.mqtt.client as mqtt
import serial
import threading
import time

import motor_driver_config as config

global running

cmd_list = {
    'set_res_3600': '01 06 00 23 0E 10',
    'rotate_3600': '01 10 00 37 00 02 04 00 00 0E 10',
    'rotate_300': '01 10 00 37 00 02 04 00 00 01 2C',
    'start_rotate': '01 06 00 4E 00 01',
    'read_current': '01 03 01 02 00 02',
    'write_current': '01 06 01 02 07 D0',
    'get_pos': '01 03 00 08 00 02',
    'unlock': '01 06 00 4F 06 00',
    'lock': '01 06 00 4F 05 00',
    'clear_pos': '01 06 00 4F 04 00',
}


def crc16_modbus(data: str) -> str:
    """
    计算给定十六进制字符串的CRC16 Modbus校验位。

    参数:
    data (str): 输入的十六进制字符串。

    返回:
    str: 生成的十六进制字符串格式的CRC校验位。
    """
    # CRC16 Modbus参数
    POLY = 0xA001  # 多项式
    crc = 0xFFFF  # 初始值

    # 将输入的十六进制字符串转换为字节数组
    bytes_data = bytes.fromhex(data)

    # 遍历每一个字节
    for byte in bytes_data:
        crc ^= byte  # 将字节与CRC寄存器进行异或
        # 遍历每一个位
        for _ in range(8):
            if (crc & 0x0001):  # 检查最低位是否为1
                crc >>= 1  # 右移1位
                crc ^= POLY  # 与多项式进行异或
            else:
                crc >>= 1  # 右移1位

    # 将CRC值转换为十六进制字符串，保持长度为4字符（2字节），并大写
    crc_hex = f"{crc:04X}"
    return crc_hex


class motor_control:
    def __init__(self):
        self.port = 'COM7'
        self.baudrate = 115200
        self.serial = None
        self.running = True
        self.read_thread = None
        self.position = 0
        self.position_data = False
        self.busy = False
        self.client = None

    def init(self):
        # 初始化串口连接
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=0.01)
            print(f'Connected to {self.port} at {self.baudrate} baud')

        except serial.SerialException as e:
            print(f'Error: {e}')

        # 初始化读写线程
        self.read_thread = threading.Thread(target=self.read_data)
        self.read_thread.start()

        # 初始化MQTT
        self.client = mqtt.Client()
        self.client.on_connect = self.mqtt_on_connect
        self.client.on_message = self.mqtt_on_message
        self.client.username_pw_set(config.MQTT_USER, config.MQTT_PASSWORD)
        self.client.connect(
            host=config.MQTT_SERVER,
            port=config.MQTT_PORT,
            keepalive=config.MQTT_KEEPALIVE
        )
        self.client.loop_start()

    def mqtt_on_connect(self, mqtt_client, userdata, flags, rc):
        if rc == 0:
            print("MQTT Connect Success!")
            mqtt_client.subscribe('spintable_1/+')
        else:
            print("Bad Connection Code: ", rc)

    def mqtt_on_message(self, mqtt_client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        if topic == 'spintable_1/control':
            self.command(payload)
        print(f'Received data from {topic}: {payload}')

    def command(self, cmd):
        if cmd == 'quit':
            self.stop()
            print('Program terminated.')
        elif cmd == 'init':
            self.init_motor()
            print('Motor Initialized.')
        elif cmd == 'rotate_360':
            self.rotate_360()
        elif cmd == 'rotate_30':
            self.rotate_30()
        elif cmd == 'zero':
            self.back_to_zero()
        elif cmd.startswith('r_'):
            angle = int(cmd[2:])
            self.rotate_angle(angle * 10)
        elif cmd == 'get_loc':
            self.get_loc()
        elif cmd == 'clear_loc':
            self.clear_loc()
        elif cmd == 'lock':
            self.lock()
        elif cmd == 'unlock':
            self.unlock()

    def read_data(self):
        while self.running:
            # if self.serial.in_waiting > 0:
            data = self.serial.readline().hex().upper()
            if data:
                if self.position_data and data.startswith('010304'):
                    hex_position = data[6:14]
                    self.position = int(hex_position, 16)
                    # 停止监听position data
                    self.position_data = False
                    print(f'Current position: {self.position}')
                print(f'Serial data: {data}')

    def stop(self):
        self.running = False
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
        if self.read_thread:
            self.read_thread.join()
        if self.serial.is_open:
            self.serial.close()
            print(f'Disconnected form {self.serial}')

    def cmd_gen(self, sequence):
        parts = sequence.split(' ')
        cmd = ''
        for part in parts:
            cmd += part
        crc = crc16_modbus(cmd)
        # 将其接到原指令末尾
        crced_cmd = cmd + crc[2:4]
        crced_cmd += crc[0:2]
        final_cmd = ' '.join(crced_cmd[i:i + 2] for i in range(0, len(crced_cmd), 2))
        return final_cmd

    def init_motor(self):
        cmds = [cmd_list['set_res_3600'],
                cmd_list['write_current'],
                cmd_list['read_current'],
                cmd_list['clear_pos']]
        self.send_data(cmds)

    def rotate_360(self):
        cmds = [cmd_list['rotate_3600'],
                cmd_list['start_rotate']]
        self.send_data(cmds)

    def rotate_30(self):
        cmds = [cmd_list['rotate_300'],
                cmd_list['start_rotate']]
        self.send_data(cmds)

    def rotate_angle(self, angle):
        angle_hex = hex(angle)[2:].upper().zfill(4)
        cmd = '01 10 00 37 00 02 04 00 00 ' + angle_hex[0:2] + ' ' + angle_hex[2:4]
        cmds = [cmd,
                cmd_list['start_rotate']]
        self.send_data(cmds)

    def back_to_zero(self):
        cmds = [cmd_list['get_pos']]
        # 告知Read线程准备读取
        self.position_data = True
        # 发送信号请求位置信息
        self.send_data(cmds)
        # 确保位置信息已经获取
        time.sleep(0.02)
        # 获得当前position
        remaining_int = 3600 - (self.position % 3600)
        remaining_hex = hex(remaining_int)[2:].upper().zfill(4)
        cmd_zero = '01 10 00 37 00 02 04 00 00 ' + remaining_hex[0:2] + ' ' + remaining_hex[2:4]
        cmds = [cmd_zero,
                cmd_list['start_rotate']]
        self.send_data(cmds)
        # 等待转回原点
        time.sleep(3)
        cmds = [cmd_list['clear_pos']]
        self.send_data(cmds)
        self.position = 0

    def get_loc(self):
        cmds = [cmd_list['get_pos']]
        # 告知Read线程准备读取
        self.position_data = True
        # 发送指令通知测量数据
        self.send_data(cmds)

    def clear_loc(self):
        cmds = [cmd_list['clear_pos']]
        self.send_data(cmds)

    def unlock(self):
        cmds = [cmd_list['unlock']]
        self.send_data(cmds)

    def lock(self):
        cmds = [cmd_list['lock']]
        self.send_data(cmds)

    def send_data(self, cmds):
        for cmd in cmds:
            send = self.cmd_gen(cmd)
            print(bytes.fromhex(send))
            self.serial.write(bytes.fromhex(send))
            time.sleep(0.01)

    def control_loop(self):
        try:
            print('''
                    Welcome to motor control system.\n
                -----------------------------------------------------------------
                    1. init: Init the system again.
                    2. rotate_360: rotate a round (clockwise).
                    3. rotate_30: rotate 30 degrees (clockwise).
                    4. zero: return to origin.
                    5. r_X: rotate X degrees (clockwise).
                    6. get_loc: get current location.
                    7. clear_loc: clear all positional parameters
                    8. lock: lock the motor.
                    9. unlock: unlock the motor.
                    Note: plase lock the motor before you proceed to next command.
                    MQTT Channel: spintable_1/control
                -----------------------------------------------------------------\n''')

            while True:
                msg = input('>>')
                m.command(msg)
                if msg == 'quit':
                    break
        except KeyboardInterrupt:
            m.command('quit')


if __name__ == '__main__':
    m = motor_control()
    m.init()
    m.init_motor()
    m.control_loop()
