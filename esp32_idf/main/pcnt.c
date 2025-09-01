#include "main.h"

static const char* TAG = "PCNT_EVENT";

// PCNT 初始化
// 注意貌似pcnt_init()这个函数名已经被内部函数占用了，如果命名为pcnt_init()会奇妙的报错
void pcnt_func_init()
{
    for(int i = 0; i <4; i++)
    {
        pcnt_unit_config_t unit_config = {
            .high_limit = 10000,
            .low_limit = -10000,
        };
        pcnt_new_unit(&unit_config, &pcnt_unit_list[i]);

        pcnt_chan_config_t chan_config = {
            .edge_gpio_num = pcnt_gpios[i],
            .level_gpio_num = -1,
        };
        pcnt_channel_handle_t pcnt_chan_handle = NULL;
        pcnt_new_channel(pcnt_unit_list[i], &chan_config, &pcnt_chan_handle);
        pcnt_channel_set_edge_action(pcnt_chan_handle, PCNT_CHANNEL_EDGE_ACTION_INCREASE, PCNT_CHANNEL_LEVEL_ACTION_KEEP);
        pcnt_unit_enable(pcnt_unit_list[i]);
        pcnt_unit_clear_count(pcnt_unit_list[i]);
        pcnt_unit_start(pcnt_unit_list[i]);
        ESP_LOGI(TAG, "PCNT channel %d has been initiated on pin %d.", i, pcnt_gpios[i]);
    }
}

// PCNT的计数器线程
void pcnt_monitor(void* params)
{
    // 获取当前计数器对应的PCNT index
    int index = *((int *) params);
    free(params);
    pcnt_unit_handle_t unit = pcnt_unit_list[index];
    
    // 空闲控制
    bool idle = false;
    while(1)
    {
        // 获取当前数字，并清除
        pcnt_unit_get_count(unit, &pcnt_count_list[index]);
        pcnt_unit_clear_count(unit);

        // 判断是否有转动指令，是否空闲，空闲时不进行测量更新
        if(motor_speed_list[index] == 0 && idle == false)
        {
            // 如果空闲，发送PCNT转速信息并停止
            char buff[64];
            sprintf(buff, "pcnt_count_%d_%d", index, pcnt_count_list[index]);
            esp_mqtt_client_publish(mqtt_client, MQTT_DATA_CHANNEL, buff, strlen(buff), 2, 0);
            pwm_set_duty(8192, index);
            pcnt_updated_list[index] = false;
            if(pcnt_count_list[index] == 0){
                idle = true;
            }
        }
        else if(motor_speed_list[index] != 0)
        {
            // 如果不空闲则开始测量
            char buff[64];
            sprintf(buff, "pcnt_count_%d_%d", index, pcnt_count_list[index]);
            esp_mqtt_client_publish(mqtt_client, MQTT_DATA_CHANNEL, buff, strlen(buff), 2, 0);
            idle = false;
            pcnt_updated_list[index] = true;
        }
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}

// PCNT 监测线程初始化
void pcnt_monitor_init()
{
    // 初始化4个PCNT监测线程
    for(int i = 0; i < 4; i++)
    {
        int* j = (int*)malloc(sizeof(int));
        if(j != NULL)
        {
            *j = i;
            if(xTaskCreate(pcnt_monitor, "PCNT_TASK", 4096, (void*) j, 1, NULL) != pdPASS)
            {
                ESP_LOGI(TAG, "PCNT monitor process %d creat failed.", *j);
                free(j);
            }
        }
    }
}