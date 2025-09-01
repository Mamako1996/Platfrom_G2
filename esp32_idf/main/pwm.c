#include "main.h"

static const char* TAG = "PWM_EVENT";

// 初始化PWM生成器
void pwm_init()
{
    // 初始化Timer定时器，作为PWM的钟
    ledc_timer_config_t ledc_timer = {
        .speed_mode         = LEDC_MODE,
        .timer_num          = LEDC_TIMER,
        .duty_resolution    = LEDC_DUTY_RES,
        .freq_hz            = LEDC_FREQ,
        .clk_cfg            = LEDC_AUTO_CLK
    };
    ledc_timer_config(&ledc_timer);
    ESP_LOGI(TAG, "PWM timer %d initiated at clock speed %d.", LEDC_TIMER, LEDC_FREQ);

    // 初始化PWM通道
    for(int i = 0; i < 4; i ++)
    {
        ledc_channel_config_t ledc_channel = {
            .speed_mode = LEDC_MODE,
            .channel    = pwm_channels[i],
            .timer_sel  = LEDC_TIMER,
            .intr_type  = LEDC_INTR_DISABLE,
            .gpio_num   = pwm_gpios[i],
            .duty       = LEDC_DUTY,
            .hpoint     = 0
        };
        ledc_channel_config(&ledc_channel);
        ESP_LOGI(TAG, "PWM channel %d initiated on port %d with max duty %d.", pwm_channels[i], pwm_gpios[i],LEDC_DUTY);
    }
}

// 改变PWM占空比方法
void pwm_set_duty(int data, int channel)
{
    // PWM频率更新
    ledc_set_duty(LEDC_MODE, pwm_channels[channel], data);
    ledc_update_duty(LEDC_MODE, pwm_channels[channel]);
    ESP_LOGI(TAG, "PWM channel %d duty set to %d.", channel, data);

    // MQTT通知
    char buff[64];
    sprintf(buff, "pwm_set_%d_%d", channel, data);
    esp_mqtt_client_publish(mqtt_client, MQTT_DATA_CHANNEL, buff, strlen(buff), 2, 0);
}