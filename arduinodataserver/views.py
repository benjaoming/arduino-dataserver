import models
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext

def render_to_response_and_add_context(template, c):
    meter_types = models.MeterType.objects.all().order_by("name")
    meters = models.Meter.objects.all()
    
    c.update({'meter_types': meter_types,
              'meters': meters,})
    
    return render_to_response(template, c)

def index(request):
    
    slideshow_meters = models.Meter.objects.exclude(default_interval=None)
    
    c = RequestContext(request, {'slideshow_meters': slideshow_meters,
                                 })
    return render_to_response_and_add_context("arduinodataserver/base.html", c)

def meter(request, meter_id):
    
    meter = get_object_or_404(models.Meter, id=meter_id)
    
    c = RequestContext(request, {'meter': meter,
                                 })
    return render_to_response_and_add_context("arduinodataserver/meter.html", c)    
