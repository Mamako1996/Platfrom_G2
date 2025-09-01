#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "esp_netif.h"
#include "esp_wifi.h"
#include "esp_err.h"
#include "esp_event.h"
#include "esp_log.h"
#include "mqtt_client.h"
#include "esp_system.h"
#include "esp_http_client.h"
#include "esp_partition.h"
#include "cJSON.h"
#include "driver/ledc.h"
#include "driver/pulse_cnt.h"


//////////////////////////////////////////////////////////////
//////////////////////// WIFI ////////////////////////////////
//////////////////////////////////////////////////////////////
// WiFi SSID and Password
// EMQX MQTT Server should be broadcasted within this network
#define WIFI_SSID "去码头整点薯条"
#define WIFI_PASS "Getfries0ndock"

// WIFI Connection Function 初始化方法
void wifi_init(void);


//////////////////////////////////////////////////////////////
//////////////////////// PWM /////////////////////////////////
//////////////////////////////////////////////////////////////
// LEDC Timer Parameters 计时器参数
#define LEDC_TIMER      LEDC_TIMER_0
#define LEDC_MODE       LEDC_LOW_SPEED_MODE
#define LEDC_DUTY_RES   LEDC_TIMER_13_BIT
#define LEDC_DUTY       (8192)
#define LEDC_FREQ       (5000)

// PWM Parameters PWM控制器参数
#define LEDC_GPIO_LIST  {5, 6, 7, 8, 9, 10}
#define LEDC_CHANNEL_LIST {LEDC_CHANNEL_0, LEDC_CHANNEL_1, LEDC_CHANNEL_2, LEDC_CHANNEL_3, LEDC_CHANNEL_4, LEDC_CHANNEL_5}
extern const int pwm_channels[6];
extern const int pwm_gpios[6];


// PWM Init Function 初始化方法
void pwm_init();
// PWM Set Duty 改变duty方法
void pwm_set_duty(int data, int channel);


//////////////////////////////////////////////////////////////
//////////////////////// PCNT ////////////////////////////////
//////////////////////////////////////////////////////////////
// PCNT Parameters 参数数组
#define PCNT_GPIO       {11, 12, 13, 14}
#define PCNT_UNIT       {NULL, NULL, NULL, NULL}
#define PCNT_UPDATE     {false, false, false, false}
#define PCNT_COUNT      {0, 0, 0, 0}

extern const int pcnt_gpios[4];
extern pcnt_unit_handle_t pcnt_unit_list[4];
extern bool pcnt_updated_list[4];
extern int pcnt_count_list[4];

// PCNT Init Function 初始化方法
void pcnt_func_init();
// PCNT Init Monitor 监测线程初始化
void pcnt_monitor_init();
// PCNT Counter 计数器线程
void pcnt_monitor(void* params);


//////////////////////////////////////////////////////////////
//////////////////////// MQTT ////////////////////////////////
//////////////////////////////////////////////////////////////
// MQTT Client 客户端
#define MQTT_CLIENT_INIT        (NULL)
// MQTT 通信信道
// CONTROL_CHANNEL 监听指令、返回控制任务接收、执行情况
#define MQTT_CONTROL_CHANNEL    "esp32_1/control"
// HEARTBEAT_CHANNEL 输出心跳
#define MQTT_HEARTBEAT_CHANNEL  "esp32_1/heartbeat"
// DATA_CHANNEL 返回PCNT转速信息、PWM更新信息
#define MQTT_DATA_CHANNEL       "esp32_1/data"

extern esp_mqtt_client_handle_t mqtt_client;

// MQTT-PID Data Struct 传参结构体
typedef struct
{
    int speed;
    int duration;
    int index;
} cmd_params;

// MQTT Connection Function 初始化方法
void mqtt_init();



//////////////////////////////////////////////////////////////
//////////////////////// Motor ///////////////////////////////
//////////////////////////////////////////////////////////////
// Motor Parameters 电机参数数组
#define MOTOR_SPEED     {0.0, 0.0, 0.0, 0.0}

extern double motor_speed_list[4];

//////////////////////////////////////////////////////////////
//////////////////////// PID /////////////////////////////////
//////////////////////////////////////////////////////////////
// PID 计算参数结构体
struct PID_params{
    // Kp - 比例参数
    double Kp;
    // Ki - 积分参数
    double Ki;
    // Kd - 微分参数
    double Kd;
    // max, min - 控制参数上、下限(PWM)
    double max_pwm;
    double min_pwm;
    // max, min - 实际转速上下限(PCNT)
    double max_pcnt;
    double min_pcnt;
};

// PID 数据参数结构体
struct PID_data{
    // integral 累计积分
    double integral;
    // 历史误差
    double pre_error;
    // 上次输入
    double pre_input;
};

// PID Calculation 计算方法
double PID_Calculate(struct PID_params params, struct PID_data *data, double target_speed, double current_speed);
// PID Controller Init Function 单控制器初始化方法
void PID_init(void* params);
// PID Process Init Function 线程初始化
void pid_process_init();
// PID Task Creation 创建一个控制任务
void control_cmd(void *params);