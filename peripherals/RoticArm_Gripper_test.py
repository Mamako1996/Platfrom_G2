from pymycobot import ElephantRobot
import time

# 测试 #1 将搅拌仓从点A移动到点B，再归位至点A
# 测试 #2 将玻璃片从台面移动到旋涂仪中，再将旋涂仪帽盖上，最后帽拿开，将玻璃片取出挂到墙壁上

elephant_client = ElephantRobot("192.168.31.197", 5001)

# 启动机器人必要指令
elephant_client.start_client()
elephant_client.set_gripper_value(50,20)
time.sleep(3)
elephant_client.set_gripper_value(0,20)