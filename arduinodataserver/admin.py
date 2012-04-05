from django.contrib import admin

import models

class DataAdmin(admin.ModelAdmin):
    list_display = ('meter', 'created', 
                    'data_point')
    
    list_filter = ('meter', 'created')

class IntervalAdmin(admin.ModelAdmin):
    list_display = ('interval_type', 'get_total', 'from_time')
    list_filter = ('interval_type', 'from_time', 'interval_type__meter_set', 'interval_type__meter_set__meter_type',)

class IntervalTypeAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.IntervalType, IntervalTypeAdmin)
admin.site.register(models.Interval, IntervalAdmin)

admin.site.register(models.MeterType)
admin.site.register(models.Meter)
admin.site.register(models.MeterData, DataAdmin)