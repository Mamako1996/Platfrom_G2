from django.db import models
from django.utils import timezone

# Create your models here.

class Task(models.Model):
    task_id = models.AutoField(primary_key=True, null=False)
    task_name = models.CharField(max_length=128, null=False)
    task_description = models.CharField(max_length=256)

class MotorControl(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    motor_name = models.CharField(max_length=128, null=False)
    motor_speed = models.IntegerField(null=False)
    time = models.DateTimeField(auto_now_add=True, null=False)

class User(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    email = models.CharField(max_length=128, null=False)
    username = models.CharField(max_length=128, null=False)
    password = models.CharField(max_length=256)
    activated = models.BooleanField(default=False)
    register_time = models.DateTimeField(auto_now_add=True, null=False)

class LoginRecord(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    email = models.CharField(max_length=128, null=False)
    login_time = models.DateTimeField(auto_now_add=True, null=False)
    token = models.CharField(max_length=512, null=False)

class Motor(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    name = models.CharField(max_length=64, null=False)
    avaliable = models.BooleanField(default=True)
    description = models.CharField(max_length=256)

DEVICE_CHOICES = (
    (1, 'ESP32S3_1'),
    (2, 'ESP32S3_2'),
    (3, 'ESP32S3_3'),
    (4, 'ESP32S3_4')
)
DEFAULT_DEVICE = 1

EVENT_STATUS = (
    (1, 'Active'),
    (2, 'Done')
)
DEFAULT_EVENT_STATUS = 1

class MotorEvent(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)
    device_id = models.IntegerField(choices=DEVICE_CHOICES, default=DEFAULT_DEVICE)
    motor = models.IntegerField(null=False)
    speed = models.IntegerField(null=False)
    time  = models.IntegerField(null=False)
    statue = models.IntegerField(choices=EVENT_STATUS, default=DEFAULT_EVENT_STATUS)


MOTOR_CHOICES = (
    (1, 'Motor_0'),
    (2, 'Motor_1'),
    (3, 'Motor_2'),
    (4, 'Motor_3'),
)
DEFAULT_MOTOR = 1
MOTOR_DATA_TYPE = (
    (1, 'PCNT'),
    (2, 'PWM')
)
DEFAULT_MOTOR_DATA = 1

class MotorData(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    timestamp = models.DateTimeField(auto_now_add=True, null=False)
    parent_event_id = models.ForeignKey(MotorEvent, on_delete=models.CASCADE)
    motor_id = models.IntegerField(choices=MOTOR_CHOICES, default=DEFAULT_MOTOR)
    data_type = models.IntegerField(choices=MOTOR_DATA_TYPE, default=DEFAULT_MOTOR_DATA)
    data = models.IntegerField(null=False)



    

class Spinning(models.Model):
    id = models.AutoField(primary_key=True, null=False)
    motor_name = models.CharField(max_length=128, null=False)
    scheduled_time = models.DateTimeField(null=False)
    motor_speed = models.IntegerField(null=False)
    duration_sec = models.IntegerField(null=False)

# class UpdateRecord(models.Model):
#     id = models.AutoField(primary_key=True, null=False)
#     time = models.DateTimeField(auto_now_add=True, null=False)
#     valid = models.BooleanField(default=False)


