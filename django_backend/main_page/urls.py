from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path(r'^tasks/$', views.task_list),
    re_path(r'^control/$', views.motor_control_list),
    re_path(r'^login/$', views.login),
    re_path(r'^signup/$', views.sign_up),
    re_path(r'^token_validation/$', views.token_validation),
    re_path(r'^user_data/$', views.get_user_data),
    re_path(r'^change_password/$', views.change_password),
    re_path(r'^get_motors/$', views.get_motors),
    re_path(r'^test/$', views.test),
    re_path(r'^spinning/$', views.spinning),
    re_path(r'^mqtt_msg/$', views.mqtt_msg),
    re_path(r'^device_list/', views.device_list),
]

urlpatterns = format_suffix_patterns(urlpatterns)