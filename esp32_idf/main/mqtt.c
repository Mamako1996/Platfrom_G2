#include "main.h"

static char* TAG = "ESP32S3_MQTT_EVENT";
static bool connect_flag = false; // 定义一个连接上mqtt服务器的flag

// MQTT信息处理
void message_compare(char *msg)
{
    if(strcmp(msg, "Hello there") == 0)
    {
        char buff[64];
        sprintf(buff, "Hello to you too");
        esp_mqtt_client_publish(mqtt_client, MQTT_CONTROL_CHANNEL, buff, strlen(buff), 2, 0);
    }
    else if(strncmp(msg, "cmd_", 4) == 0)
    {
        int index, speed, duration;
        sscanf(msg, "cmd_%d_%d_%d",  &index, &speed, &duration);
        cmd_params params = {speed, duration, index};
        xTaskCreate(control_cmd, "CMD_TASK", 4096, (void*)&params, 1, NULL);

    }
}

// MQTT事件处理回调函数
static void mqtt_event_handler(void *args, esp_event_base_t base, int32_t id, void *event_data)
{
    // 获取MQTT客户端信息
    esp_mqtt_event_t *client_event = event_data;
    esp_mqtt_event_id_t client_id = id;

    // 判断MQTT具体事件
    switch (client_id)
    {
        case MQTT_EVENT_CONNECTED:
            ESP_LOGI(TAG, "Connected to MQTT server.");
            connect_flag = true;
            // 订阅MQTT 控制频道来接收指令
            esp_mqtt_client_subscribe(mqtt_client, MQTT_CONTROL_CHANNEL, 2);
            break;

        case MQTT_EVENT_DISCONNECTED:
            ESP_LOGI(TAG, "Disconnected from MQTT server.");
            connect_flag = false;
            break;

        case MQTT_EVENT_DATA:
            {
                // 接收外部传入的信息，分别存储topic和data
                char topic[128] = {};
                char data[512] = {};
                memcpy(topic, client_event->topic, client_event->topic_len);
                memcpy(data, client_event->data, client_event->data_len);
                // 进行信息处理，目前只传入了data而没有传入topic
                message_compare(data);
            }
            break;
        case MQTT_EVENT_ERROR:
            ESP_LOGE(TAG, "MQTT connection error");
            connect_flag = false;
            break;

        default:
            break;
    }
}


// 初始化MQTT线程
void mqtt_init()
{
    // mqtt服务器的配置信息
    esp_mqtt_client_config_t cfg = {
        .broker.address = {
            // EMQX 服务器主机IP地址
            .uri = "mqtt://192.168.31.74",
            .port = 1883,
            
        },
        .credentials = {
            .username = "ESP32_1",
            
        },
        .credentials.authentication = {
            .password = "123456",
        }
    };

    // 定义MQTT客户端
    mqtt_client = esp_mqtt_client_init(&cfg);

    //注册MQTT状态机事件处理回调函数
    esp_mqtt_client_register_event(mqtt_client, MQTT_EVENT_ANY, mqtt_event_handler, NULL);

    // 开始MQTT客户端
    esp_mqtt_client_start(mqtt_client);

    // 客户端心跳
    while (1)
    {
        if (connect_flag == true)
        {
            char buff[64] = "ESP32_1 is online";
            // 向mqtt服务器发布主题为heartbeat，payload为buff的数据
            esp_mqtt_client_publish(mqtt_client, MQTT_HEARTBEAT_CHANNEL, buff, strlen(buff), 2, 0); 
        }

        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}