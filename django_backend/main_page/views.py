from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Task, MotorControl, User, Motor, Spinning
from .serializer import TaskSerializer, MotorControlSerializer, UserSerializer, LoginRecordSerializer, \
    SpinningSerializer
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone

from .token import create_token, check_token, token_auth

from .mqtt import client as mqtt_client

import requests
import base64


@api_view(['GET', 'POST'])
def task_list(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


@api_view(['GET', 'POST'])
def motor_control_list(request):
    if request.method == 'POST':
        serializer = MotorControlSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'GET':
        controls = MotorControl.objects.all()
        serializer = MotorControlSerializer(controls, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def login(request):
    user = User.objects.filter(email=request.data['email'])
    if user:
        encoded = user[0].password
        if check_password(request.data['password'], encoded):
            token = create_token(request.data['email'])
            login_record_s = LoginRecordSerializer(data={'email': request.data['email'], 'token': token})
            if login_record_s.is_valid():
                login_record_s.save()
            else:
                print(login_record_s.errors)
            return Response({'Login Success': 'Login Success', 'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'Login Failed': 'Wrong Password!'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'Login Failed': 'User Does Not Exist!'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def sign_up(request):
    data = request.data
    # Encript the password using hashing
    data['password'] = make_password(data['password'])
    serializer = UserSerializer(data=data)
    if User.objects.filter(email=data['email']).exists():
        return Response({'Registration Failed': 'User Already Exists!'}, status=status.HTTP_400_BAD_REQUEST)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def token_validation(request):
    result = check_token(request.data['token'])
    if result == 'expired':
        return Response({'Token validation': 'Expired'}, status=status.HTTP_403_FORBIDDEN)
    elif result == 'fail':
        return Response({'Token validation': 'Failed'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'Token validation': 'Success', 'email': result['email']}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_user_data(request):
    if (request.data['token']):
        if token_auth(request.data['token']):
            data = User.objects.filter(email=request.data['email']).values()[0]
            del data['password']
            del data['id']
            return JsonResponse(data=data, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_password(request):
    if token_auth(request.data['token']):
        user = User.objects.filter(email=request.data['email'])[0]
        if user:
            encoded = user.password
            if check_password(request.data['old_password'], encoded):
                new_password = make_password(request.data['new_password'])
                user.password = new_password
                user.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response({'Password change fail': 'Old password wrong'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_motors(request):
    if token_auth(request.data['token']):
        motors = []
        for motor in Motor.objects.all().values():
            motors.append(motor)
        return Response({'motor_list': motors}, status.HTTP_200_OK)
    return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def spinning(request):
    if token_auth(request.data['token']):
        if request.data['data']:
            spin_instance = request.data['data']
            print(spin_instance)
            if spin_instance['motor_name']:
                spin_instance['scheduled_time'] = datetime.strptime(spin_instance['scheduled_time'],
                                                                    '%Y-%m-%dT%H:%M:%S')
                # print(spin_instance)
                spin_ser = SpinningSerializer(data=spin_instance)
                if spin_ser.is_valid():
                    spin_ser.save()
                    return Response(status.HTTP_200_OK)
            return Response(status.HTTP_400_BAD_REQUEST)
        else:
            records = []
            for record in Spinning.objects.all().values():
                records.append(record)
                record['scheduled_time'] = timezone.localtime(record['scheduled_time'])
                # print(record)
            return Response({'record_list': records}, status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def test(request):
    records = []
    for record in Spinning.objects.all().values():
        temp = {
            'id': record['id'],
            'time': timezone.localtime(record['scheduled_time']).timestamp(),
            'speed': record['motor_speed'],
            'duration': record['duration_sec']
        }
        records.append(temp)
    return Response({'now': timezone.localtime().timestamp(), 'data': records}, status=status.HTTP_200_OK)


# MQTT View
@api_view(['GET', 'POST'])
def mqtt_msg(request):
    if request.method == 'POST':
        if (request.data['topic']):
            topic = request.data['topic']
            msg = request.data['msg'] * 6
            msg = 'pwm_' + str(msg)
            # return Response(status=status.HTTP_200_OK)
            rc, mid = mqtt_client.publish(topic, msg)
            return JsonResponse({'code': rc})
        else:
            return Response({'request fail': 'Deined'}, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET':
        motor_speed = MotorControl.objects.values().last()['motor_speed']
        return Response({'speed': motor_speed}, status=status.HTTP_200_OK)


# Device List
@api_view(['GET'])
def device_list(request):
    # 限制只接受一页，并且每页上限50个设备
    url = "http://localhost:18083/api/v5/clients?page=1&limit=50&node=emqx%40127.0.0.1"
    # EMQX 的密钥信息
    api_key = "14d39e44d739b1d9"
    secret_key = "DrXETy29CGKJnUHWMTQauKnOYzBN9A65z5Yw4FiUMpt9BC"

    # 使用Base64方式加密密钥对
    credentials = f"{api_key}:{secret_key}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + encoded_credentials
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 如果响应码不是200，会抛出异常

        # 获取连接信息
        connections = response.json()
        return JsonResponse(connections, safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': str(e)}, status=500)
