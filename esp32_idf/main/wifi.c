#include "main.h"

static char *TAG = "ESP32S3_WIFI_EVENT";

// 互斥信号量，作为保护，其实就是监测这个进程是否完成
SemaphoreHandle_t sem;

static void event_handler(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data)
{
    if ((event_base == WIFI_EVENT) && (event_id == WIFI_EVENT_STA_START ||
                                       event_id == WIFI_EVENT_STA_DISCONNECTED))
    {
        ESP_LOGI(TAG, "Begin to connect the AP");
        esp_wifi_connect();
    }
    else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP)
    {
        ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
        ESP_LOGI(TAG, "Got ip:" IPSTR, IP2STR(&event->ip_info.ip));
        xSemaphoreGive(sem);
    }
}

void wifi_init(void)
{
    // 初始化阶段

    // 初始化sem
    sem = xSemaphoreCreateBinary();
    // 初始化NVS Flash内存
    ESP_ERROR_CHECK(nvs_flash_init());
    // 事件循环初始化
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    // 注册相应句柄
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, event_handler, NULL));
    // 初始化netif
    ESP_ERROR_CHECK(esp_netif_init());
    // 创建wifi station
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t wifi_cfg = WIFI_INIT_CONFIG_DEFAULT();
    // 初始化wifi
    ESP_ERROR_CHECK(esp_wifi_init(&wifi_cfg));

    // 配置阶段

    // 配置WiFi station 模式
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    // 配置WiFi信息
    wifi_config_t cfg = {
        .sta = {
            .ssid = WIFI_SSID,
            .password = WIFI_PASS,
        }};
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &cfg));

    // 启动阶段
    ESP_ERROR_CHECK(esp_wifi_start());

    // 等待阶段
    while (1)
    {
        if (xSemaphoreTake(sem, portMAX_DELAY) == pdPASS)
        {
            ESP_LOGI(TAG, "Connected to ap!");
            break;
        }
    }

}
