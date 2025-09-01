from django.contrib import admin

# Register your models here.

from .models import Task, MotorControl, User, LoginRecord, Motor, Spinning, MotorEvent, MotorData

class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'task_description')

class MotorControlAdmin(admin.ModelAdmin):
    list_display = ('motor_name', 'motor_speed', 'time')
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'register_time')

class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ('email', 'login_time')

class MotorAdmin(admin.ModelAdmin):
    list_display = ('name', 'avaliable')

class SpinningAdmin(admin.ModelAdmin):
    list_display = ('motor_name', 'scheduled_time', 'motor_speed', 'duration_sec')

class MotorEventAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'motor', 'speed', 'time', 'statue', 'timestamp')

class MotorDataAdmin(admin.ModelAdmin):
    list_display = ('data_type', 'data', 'parent_event_id', 'timestamp')

admin.site.register(Task, TaskAdmin)
admin.site.register(MotorControl, MotorControlAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(LoginRecord, LoginRecordAdmin)
admin.site.register(Motor, MotorAdmin)
admin.site.register(Spinning, SpinningAdmin)
admin.site.register(MotorEvent, MotorEventAdmin)
admin.site.register(MotorData, MotorDataAdmin)