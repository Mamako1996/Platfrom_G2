import sqlite3, time, threading
from datetime import datetime, timedelta
from paho.mqtt import client as mqtt

task_finished = False


# MQTT 相关组件
def mqtt_on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connect Success!")
        mqtt_client.subscribe('task_manager')
    else:
        print("Bad Connection Code: ", rc)


def mqtt_on_message(mqtt_client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    print(f'[{topic}]: {payload}')
    if payload == 'Task Finished.':
        global task_finished
        task_finished = True


class Task_Manager():
    def __init__(self):
        self.conn = None
        self.c = None
        self.first_task = None
        self.terminate = False
        self.task_triggered = False
        self.mqtt_client = None

    # 整体控制初始化
    def manager_init(self):
        self.mqtt_init()
        threading.Thread(target=self.update_thread).start()
        threading.Thread(target=self.timer_thread).start()
        threading.Thread(target=self.mqtt_heartbeat).start()
        self.user_input()

    # 数据库相关组件
    def database_connect(self):
        self.conn = sqlite3.connect('db.sqlite3')
        self.c = self.conn.cursor()

    def database_disconnect(self):
        self.conn.close()

    def update_time_schedule(self):
        local_first_task = None
        self.c.execute('select COUNT(*) from main_page_spinning')
        row_num = self.c.fetchone()
        results = self.c.execute('select * from main_page_spinning')
        # 监测库中是否有未完成项目
        if row_num[0] > 0:
            for row in results:
                if local_first_task == None:
                    local_first_task = row
                elif datetime.strptime(local_first_task[2], '%Y-%m-%d %H:%M:%S') > datetime.strptime(row[2],
                                                                                                     '%Y-%m-%d %H:%M:%S'):
                    local_first_task = row
            # 将UTC转化成UTC+8
            UTC = datetime.strptime(local_first_task[2], '%Y-%m-%d %H:%M:%S')
            UTC_8 = UTC + timedelta(hours=8)
            # 将tuple类型转化成list类型方便修改
            tmp = local_first_task
            local_first_task = []
            for item in tmp:
                local_first_task.append(item)
            # 修改时间参数
            local_first_task[2] = UTC_8.strftime('%Y-%m-%d %H:%M:%S')
            if self.first_task == None:
                self.first_task = local_first_task
                self.task_triggered = False
                record_update = 'Updated First Task Detial: \n' + str(self.first_task)
                print(record_update)
                self.mqtt_client.publish('task_manager', record_update)
            else:
                if datetime.strptime(self.first_task[2], '%Y-%m-%d %H:%M:%S') != UTC_8:
                    self.first_task = local_first_task
                    self.task_triggered = False
                    record_update = 'Updated First Task Detial: \n' + str(self.first_task)
                    print(record_update)
                    self.mqtt_client.publish('task_manager', record_update)
        else:
            self.first_task = None

    # 更新数据线程
    def update_thread(self):

        while not self.terminate:
            self.database_connect()
            # 监测任务是否完成
            global task_finished
            if task_finished == True:
                sql_cmd = 'delete from main_page_spinning where id=' + str(self.first_task[0]) + ';'
                self.c.execute(sql_cmd)
                self.conn.commit()
                task_finished = False
            self.update_time_schedule()
            self.database_disconnect()
            time.sleep(1)

    # 触发器线程
    def timer_thread(self):
        while not self.terminate:
            time.sleep(0.1)
            if self.first_task == None:
                pass
            else:
                if (datetime.now() > datetime.strptime(self.first_task[2],
                                                       '%Y-%m-%d %H:%M:%S')) and not self.task_triggered:
                    timer_trigger = 'Timer at ' + str(self.first_task[2]) + ' has be triggered. Current time is ' + str(
                        datetime.now())
                    print(timer_trigger)
                    self.mqtt_client.publish('task_manager', timer_trigger)
                    self.task_triggered = True
                    cmd = 'cmd_' + str(self.first_task[3]) + '_' + str(self.first_task[4]) + '_0'
                    self.mqtt_client.publish('control', cmd)

    # MQTT 初始化方法
    def mqtt_init(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = mqtt_on_connect
        self.mqtt_client.on_message = mqtt_on_message
        self.mqtt_client.username_pw_set('Task_Manager_py', '123456')
        self.mqtt_client.connect(
            host='192.168.31.18',
            port=1883,
            keepalive=60
        )

    # MQTT心跳，告知客户端连接状态
    def mqtt_heartbeat(self):
        self.mqtt_client.loop_start()
        while not self.terminate:
            self.mqtt_client.publish('heartbeat/task_manager', 'Status: Alive')
        self.mqtt_client.loop_stop()

    # 用户操作界面
    def user_input(self):
        while not self.terminate:
            usr_in = input('What do you want?\n')
            if usr_in == 'quit()':
                self.terminate = True
            elif usr_in == 'get_first_task':
                print(self.first_task)


if __name__ == '__main__':
    tm = Task_Manager()
    tm.manager_init()
