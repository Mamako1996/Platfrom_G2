from pymycobot import ElephantRobot
from robo_arm_config import IP_ADDRESS, PORT, CORD_LIST


class RoboArmControl:
    def __init__(self):
        self.client = ElephantRobot(IP_ADDRESS, PORT)
        self.client.start_client()
        self.running = True

    def end(self):
        self.client.stop_client()

    def to_position(self, angle_list, speed):
        try:
            self.client.write_angles(angle_list, speed)
            # 我也不知道他会打印什么东西
            response = self.client.command_wait_done()
            print(response)
            print(self.client.get_coords())
            print(self.client.get_angles())
            return 'Success'
        except:
            return 'Fail'

    def to_zero(self):
        # print(CORD_LIST['zero'])
        self.to_position(CORD_LIST['zero'], 1000)
        self.print_position()

    def print_position(self):
        try:
            print(self.client.get_coords())
            print(self.client.get_angles())
            print(self.client.get_speed())
            return 'Success'
        except:
            return 'Fail'

    def route(self, route, speed):
        for point in route:
            self.to_position(point, speed)

    def main_loop(self):
        while self.running:
            cmd = input('>>>')
            if cmd == 'quit':
                self.end()
                self.running = False
            elif cmd == 'get_pos':
                self.print_position()
            elif cmd == 'to_zero':
                self.to_zero()
            elif cmd == 'r_1':
                self.route(CORD_LIST['route_1'], 1000)
            elif cmd == 'r_2':
                self.route(CORD_LIST['route_2'], 1500)


if __name__ == '__main__':
    control = RoboArmControl()
    control.main_loop()
