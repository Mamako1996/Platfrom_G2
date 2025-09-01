# 注意到如果我们直接使用通常的python manage.py runserver 0.0.0.0:8000会造成创建了两个MQTT Client
# 这是因为Django会创建两个线程，其中一个是主线程，另外一个是支线程用来在必要的时候刷新你的主线程
# 所以说我们可以在开启server的时候直接将支线程ban掉，即使用 --noreload指示
# 当然这么做我也不知道会不会对其他的东西产生影响，所以说我们可以通过以下Stack Overflow的回答来规避
# https://stackoverflow.com/questions/33814615/how-to-avoid-appconfig-ready-method-running-twice-in-django
# 依照上面给出的回答我们添加 if os.environ.get('RUN_MAIN') 判断即可规避掉在支线程当中的任何操作
# MQTT后端当中显示的连接数也变成2

import paho.mqtt.client as mqtt
from django.conf import settings
import os

from django.apps import apps

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import MotorEvent, MotorData

ongoing_events = []


def on_connect(mqtt_client, userdata, flags, rc):
    if rc == 0:
        print("MQTT Connect Success!")
        mqtt_client.subscribe('esp32_1/+')
    else:
        print("Bad Connection Code: ", rc)


# Django 存储方法
# Device事件开始
def device_event_start(device_id, motor, speed, time):
    global ongoing_events
    # objects.create()方法返回一个新建立的object
    device_event = MotorEvent.objects.create(
        device_id=device_id,
        motor=motor,
        speed=speed,
        time=time,
    )
    ongoing_events.append(device_event)


# Motor接收数据
def device_data(device_id, motor, data_type, data):
    global ongoing_events
    for event in ongoing_events:
        # 判定当前接收数据与正在进行事件列表中哪一个事件契合
        if event.motor == motor and event.device_id == device_id:
            MotorData.objects.create(
                parent_event_id=event,
                motor_id=motor,
                data_type=data_type,
                data=data
            )
        else:
            pass


# Device事件结束
def device_event_done(device_id, motor):
    global ongoing_events
    tmp_array = []
    for event in ongoing_events:
        if event.motor == motor and event.device_id == device_id:
            # 更新事件状态
            event.statue = 2
            event.save()
        else:
            # 保留
            tmp_array.append(event)
    # 更新仍在进行的事件列表
    ongoing_events = tmp_array


def on_message(mqtt_client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    channel_layer = get_channel_layer()
    if msg.topic.startswith('esp32_1/'):
        # MQTT指令信号
        # cmd_motor_speed_time
        if payload.startswith('cmd_'):
            payload = payload.replace('cmd_', '').strip()
            parts = payload.split('_')
            motor = int(parts[0])
            speed = int(parts[1])
            time = int(parts[2])
            package = {
                'type': 'mqtt_msg_broadcast',
                'device': 1,
                'topic': 'cmd',
                'motor': motor,
                'speed': speed,
                'time': time
            }
            # 将收到的异步信息以同步的形式发送到Websocket接收端（consumer.py）
            async_to_sync(channel_layer.group_send)('mqtt_group', package)

        # ESP32反馈PCNT数据
        # pcnt_count_motor_data
        elif payload.startswith('pcnt_count_'):
            payload = payload.replace('pcnt_count_', '').strip()
            parts = payload.split('_')
            motor = int(parts[0])
            count = int(parts[1])
            package = {
                'type': 'mqtt_msg_broadcast',
                'device': 1,
                'topic': 'pcnt',
                'motor': motor,
                'pcnt': count
            }
            # 创建Motor PCNT数据词条
            device_data(1, motor, 1, count)
            async_to_sync(channel_layer.group_send)('mqtt_group', package)

        # ESP32反馈PWM数据
        # pwm_set_motor_data
        elif payload.startswith('pwm_set_'):
            payload = payload.replace('pwm_set_', '').strip()
            parts = payload.split('_')
            motor = int(parts[0])
            count = int(parts[1])
            package = {
                'type': 'mqtt_msg_broadcast',
                'device': 1,
                'topic': 'pwm',
                'motor': motor,
                'pwm': count
            }
            # 创建Motor PWM数据词条
            device_data(1, motor, 2, count)
            async_to_sync(channel_layer.group_send)('mqtt_group', package)

        # ESP32反馈任务相关信号
        # task_create_motor_speed_time
        # task_finished_motor_speed_time
        elif payload.startswith('task_'):
            payload = payload.replace('task_', '').strip()
            # ESP32接到任务
            if payload.startswith('create_'):
                payload = payload.replace('create_', '').strip()
                parts = payload.split('_')
                motor = int(parts[0])
                speed = int(parts[1])
                time = int(parts[2])
                package = {
                    'type': 'mqtt_msg_broadcast',
                    'device': 1,
                    'topic': 'task_create',
                    'motor': motor,
                    'speed': speed,
                    'time': time
                }
                # Device列表创建任务
                device_event_start(1, motor, speed, time)
                async_to_sync(channel_layer.group_send)('mqtt_group', package)
            # ESP32完成任务
            elif payload.startswith('finished_'):
                payload = payload.replace('finished_', '').strip()
                parts = payload.split('_')
                motor = int(parts[0])
                package = {
                    'type': 'mqtt_msg_broadcast',
                    'device': 1,
                    'motor': motor,
                    'topic': 'task_done',
                }
                device_event_done(1, motor)
                async_to_sync(channel_layer.group_send)('mqtt_group', package)


if os.environ.get('RUN_MAIN'):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
    client.connect(
        host=settings.MQTT_SERVER,
        port=settings.MQTT_PORT,
        keepalive=settings.MQTT_KEEPALIVE
    )
