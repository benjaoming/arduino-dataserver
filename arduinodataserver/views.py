import models
from django.shortcuts import render_to_response
from django.template.context import RequestContext

def index(request):
    
    meter_types = models.MeterType.objects.all().order_by("name")
    
    slideshow_meters = models.Meter.objects.exclude(default_interval=None)
    
    meters = models.Meter.objects.all()
    
    c = RequestContext(request, {'meter_types': meter_types,
                                 'slideshow_meters': slideshow_meters,
                                 'meters': meters,})
    return render_to_response("arduinodataserver/base.html", c)
