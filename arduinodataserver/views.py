import models
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from datetime import datetime, date
from django.core.serializers import json
from django.http import HttpResponse

def render_to_response_and_add_context(template, c):
    meter_types = models.MeterType.objects.all().order_by("name")
    meters = models.Meter.objects.all()
    
    c.update({'meter_types': meter_types,
              'meters': meters,})
    
    return render_to_response(template, c)

def index(request):
    
    slideshow_meters = models.Meter.objects.exclude(default_interval=None).order_by('name')
    
    c = RequestContext(request, {'slideshow_meters': slideshow_meters,
                                 })
    return render_to_response_and_add_context("arduinodataserver/base.html", c)

def meter(request, meter_id):
    
    meter = get_object_or_404(models.Meter, id=meter_id)
    
    c = RequestContext(request, {'meter': meter,
                                 })
    return render_to_response_and_add_context("arduinodataserver/meter.html", c)    

def interval_json(request, interval_type_id, max_entries=24, hide_unfinished=0):
    
    interval_type = get_object_or_404(models.IntervalType, id=interval_type_id)
    intervals = models.Interval.objects.filter(interval_type=interval_type)
    
    from_date = request.GET.get('from_date', None)
    if from_date:
        from_date = datetime.strptime("%s 00:00" % from_date, "%Y-%m-%d %H:%M")
        intervals = intervals.filter(from_time__gte=from_date)
        
    to_date = request.GET.get('to_date', None)
    if to_date:
        to_date = datetime.strptime("%s 00:00" % to_date, "%Y-%m-%d %H:%M")
        intervals = intervals.filter(to_time__lte=to_date)
    
    intervals = intervals.order_by('-from_time')
    max_entries = max_entries or request.GET.get('entries', None)
    if max_entries:
        intervals = intervals[:max_entries]
    intervals = intervals.reverse()

    def get_google_date(datetimeobj):
        return "Date(%d, %d, %d, %d, %d, %d, %d)" % (datetimeobj.year,
                                                     datetimeobj.month-1,
                                                     datetimeobj.day,
                                                     datetimeobj.hour,
                                                     datetimeobj.minute,
                                                     datetimeobj.second+1,
                                                     datetimeobj.microsecond/1000) 
    
    data = json.simplejson.dumps({
             "cols": [
                      {"id": "","label": "", "pattern": "", "type": "datetime"},
                      {"id": "","label": interval_type.unit_name, "pattern": "", "type":"number"}
                      ],
             "rows": [({"c": [{"v": get_google_date(i.to_time)},
                              {"v": i.total}]}) for i in intervals],
           })
    return HttpResponse(data, mimetype='application/json')
