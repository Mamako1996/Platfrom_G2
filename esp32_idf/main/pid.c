#include "main.h"

static const char* TAG = "PID_EVENT";

// 这里的PID控制针对于以下过程
// -- 转速 --> PID 控制器 --> PWM 控制输入 --> PCNT 转速测量 -->
//          ^                                     |
//          |                                     |
//          ---------------------------------------
double PID_Calculate(struct PID_params params, struct PID_data *data, double target_speed, double current_speed)
{
    // 计算Error
    double error = target_speed - current_speed;

    // 比例项
    double Pout = params.Kp * error;
    
    // 积分项
    data -> integral += error;
    // 限制积分项，防止积分饱和
    if(data -> integral > params.max_pwm)
    {
        data -> integral = params.max_pwm;
    }
    if(data -> integral < params.min_pwm)
    {
        data -> integral = params.min_pwm;
    }
    double Iout = params.Ki * data -> integral;

    // 微分项
    double derivative = (error - data -> pre_error);
    double Dout = params.Kd * derivative;

    // 计算整体输出
    double output = Pout + Iout + Dout;
    output = data -> pre_input + output;

    // 限制条件
    if(output > params.max_pwm)
    {
        output = params.max_pwm;
    }
    else if(output < params.min_pwm)
    {
        output = params.min_pwm;
    }

    // 保存本次误差到上次
    data -> pre_error = error;
    data -> pre_input = output;

    return output;
}

// 初始化PID控制器
void PID_init(void* params)
{
    // 获取外部参数
    int index = *((int *) params);
    ESP_LOGI(TAG, "Index number is: %d\n", index);
    // 释放内存
    free(params);

    struct PID_data data = {
        .integral   = 0,
        .pre_error  = 0,
        .pre_input = 0
    };

    struct PID_params pid_params = {
        .Kp         = 8,
        .Ki         = 0.02,
        .Kd         = 0.01,
        .max_pwm    = 8192,
        .min_pwm    = 0,
        .max_pcnt   = 435,
        .min_pcnt   = -435
    };

    while(1){
        if(pcnt_updated_list[index] == true)
        {
            double temp = motor_speed_list[index];
            double new_input = PID_Calculate(pid_params, &data, temp, pcnt_count_list[index]);
            int new_input_int = 8192 - (int)new_input;
            pwm_set_duty(new_input_int, index);
            pcnt_updated_list[index] = false;
        }
        else{
            vTaskDelay(10 / portTICK_PERIOD_MS);
        }
    }
}

void pid_process_init()
{
    for(int i = 0; i < 4; i++)
    {
        // 动态分配所需的内存空间
        int *j = (int *)malloc(sizeof(int));
        if(j != NULL)
        {
            *j = i;
            // 创建线程
            if(xTaskCreate(PID_init, "PID_TASK", 4096, (void*) j, 1, NULL) != pdPASS)
            {
                // 如果失败，释放内存
                ESP_LOGI(TAG, "PID process %d creation failed.", *j);
                free(j);
            }
        }
    }
}


// 创建一个控制任务
void control_cmd(void *params)
{
    cmd_params* local_params = (cmd_params*)params;
    int local_speed = local_params -> speed;
    int local_duration = local_params -> duration;
    int local_index = local_params -> index;

    char buff[64];
    sprintf(buff, "task_create_%d_%d_%d",local_index, local_speed, local_duration);
    esp_mqtt_client_publish(mqtt_client, MQTT_CONTROL_CHANNEL, buff, strlen(buff), 2, 0);
    motor_speed_list[local_index] = local_speed;
    vTaskDelay(local_duration * 1000 / portTICK_PERIOD_MS);
    motor_speed_list[local_index] = 0;
    pwm_set_duty(8192, local_index);
    sprintf(buff, "task_finished_%d_%d_%d",local_index, local_speed, local_duration);
    esp_mqtt_client_publish(mqtt_client, MQTT_CONTROL_CHANNEL, buff, strlen(buff), 2, 0);
    vTaskDelete(NULL);
}



