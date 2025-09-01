import time
import serial
import math
import KSY30_pump_config as config

DT_cmd_test_list = {
    "Active": 'QR',
    "Init": 'ZR',
    "In_2.5ml": 'IA24000R',
    "Inlet_to_outlet": 'IA24000M10000A0M1000R',
    "Three_loops_test": 'IA24000M10000A0M1000G3R',
    "Split_drainage": 'IA24000M10000A12000M1000A0R',
    "Current_location": "2f313f340d"
}


def DT_cmd_to_byte(input_string):
    # 将每个字符转换为 ASCII 值，并以十六进制格式显示
    b_cmd = "/1" + input_string + "\r"
    byte_array = bytes([ord(char) for char in b_cmd])
    # print(byte_array)
    return byte_array


def init():
    # 配置串口
    ser = serial.Serial('COM6', 9600, timeout=1)
    try:
        if not ser.is_open:
            ser.open()

        # 发送字节序列
        ser.write(DT_cmd_to_byte(DT_cmd_test_list["Active"]))

        # 查看串口是否返回正确启动信息
        resp = ser.readline()
        if str(resp.hex()) == "2f306767030d0a" or "2f306060030d0a":
            print("Available")
            time.sleep(1)
            ser.write(bytes.fromhex(DT_cmd_test_list["Current_location"]))
            print(ser.readline())
            if str(ser.readline()) == "2f30603234303030030d0a":
                ser.write(DT_cmd_to_byte(DT_cmd_test_list["Init"]))
                time.sleep(8)
                ser.write(DT_cmd_to_byte(DT_cmd_test_list["In_2.5ml"]))
                time.sleep(8)
                ser.write(DT_cmd_to_byte(DT_cmd_test_list["Init"]))
            else:
                ser.write(DT_cmd_to_byte(DT_cmd_test_list["In_2.5ml"]))
                time.sleep(8)
                ser.write(DT_cmd_to_byte(DT_cmd_test_list["Init"]))
                time.sleep(8)
        else:
            print(resp.hex())
            return False
    except serial.SerialException as error:
        print(f"Error: {error}")

    # 阀门校准加预备三联

    return True


def Volumetric_Converter(vol):
    # 用于将加液计量换算成步进电机步数
    vol = config.REGRESSION_COEFFICIENT * vol + config.INTERCEPT
    vol = round(vol, 4)
    print(vol)
    unit_vol = config.FULL_STEPS / config.CHAMBER_VOL
    # 等待1s=1000ms
    wait = 1000
    if vol < 0:
        raise ValueError("Dosage should be a positive number.")
    else:
        # 当输入计量大于腔体最大容积，需要多次往返
        if vol > config.CHAMBER_VOL:
            num_loops = math.floor(vol / config.CHAMBER_VOL)

            # 当输入的容积不为腔体最大容积的整数倍时，最后一次往返按需推进
            if vol % config.CHAMBER_VOL != 0:
                remains = int((vol - num_loops * config.CHAMBER_VOL) * unit_vol)
                if num_loops != 1:
                    loops = "G" + str(num_loops)  # G3 意味着重复三次之前的指令
                else:
                    loops = ""
                cmd = "IA" + str(config.FULL_STEPS) + "M" + str(wait) + "OAO" + loops + "M" + str(wait) + "IA" + str(
                    remains) + "OAO" + "R"  # IA：进液 OAO：出液 M：停几秒 R：收尾命令字符
            else:
                loops = "G" + str(num_loops)
                cmd = "IA" + str(config.FULL_STEPS) + "M" + str(wait) + "OAO" + loops + "M1000" + "R"
        else:
            cmd = "IA" + str(int(vol * unit_vol)) + "M" + str(wait) + "OAO" + "R"
    print(cmd)
    return cmd


def injection(vol):
    ser = serial.Serial('COM6', 9600, timeout=1)
    try:
        if not ser.is_open:
            ser.open()
        print(DT_cmd_to_byte(Volumetric_Converter(vol)))
        ser.write(DT_cmd_to_byte(Volumetric_Converter(vol)))

    except serial.SerialException as error:
        print(f"Error: {error}")


if __name__ == '__main__':
    injection(6)

# round 4 1.25ml->1.2475g [1.257, 1.255, 1.257, 1.254, 1.256]

# 1.25ml->1.2475g [1.255, 1.255, 1.254, 1.256, 1.255] / 0.52% ~ 0.68%

# 3.00ml->2.994g [3.022, 3.018, 3.020, 3.018, 3.018] / 0.80% ~ 0.94%

# 6.00ml->5.988g [6.048, 6.045, 6.048, 6.031, 6.043] / 0.72% ~ 1.00%
