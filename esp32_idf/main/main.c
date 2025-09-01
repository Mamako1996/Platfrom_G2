#include "main.h"

//////////////////////////////////////////////////////////////
//////////////////////// Data Init ///////////////////////////
//////////////////////////////////////////////////////////////
// MQTT 客户端初始化
esp_mqtt_client_handle_t mqtt_client = MQTT_CLIENT_INIT;

// Motor 控制数组初始化
double motor_speed_list[4] = MOTOR_SPEED;

// PWM 参数组初始化
// PWM GPIO 信道初始化
const int pwm_gpios[6] = LEDC_GPIO_LIST;
// PWM 频道初始化
const int pwm_channels[6] = LEDC_CHANNEL_LIST;

// PCNT参数组初始化
// PCNT GPIO 信道初始化
const int pcnt_gpios[4] = PCNT_GPIO;
// PCNT 单元回调函数初始化
pcnt_unit_handle_t pcnt_unit_list[4] = PCNT_UNIT;
// PCNT 计数数组初始化
int pcnt_count_list[4] = PCNT_COUNT;
// PCNT 更新数组初始化
bool pcnt_updated_list[4] = PCNT_UPDATE;

// 主函数
void app_main(void){
    // 初始化WiFi，并等待WiFi连接
    wifi_init();
    vTaskDelay(5000 / portTICK_PERIOD_MS);
    // 创建mqtt线程
    xTaskCreate(mqtt_init, "MQTT_TASK", 4096, NULL, 1, NULL);
    // 初始化PWM
    pwm_init();
    // 初始化PCNT
    pcnt_func_init();
    // 创建PCNT计数线程
    pcnt_monitor_init();
    // 初始化pid线程
    pid_process_init();

    // 防止主线程结束
    while(1)
    {
        vTaskDelay(5000 / portTICK_PERIOD_MS);
    }
}
