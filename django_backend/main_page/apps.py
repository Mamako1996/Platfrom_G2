from django.apps import AppConfig
import os

class MyAppConfig(AppConfig):
    name = 'main_page'

    def ready(self):
        if os.environ.get('RUN_MAIN'):
            from . import mqtt
            mqtt.client.loop_start()
