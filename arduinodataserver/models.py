from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save

from datetime import timedelta
from calendar import monthrange

import signal_receivers

(INTERVAL_HOURLY,
 INTERVAL_DAILY,
 INTERVAL_WEEKLY,
 INTERVAL_MONTHLY,
 INTERVAL_ANNUALLY) = range(5)

INTERVALS = [
    (INTERVAL_HOURLY,   _('hourly')),
    (INTERVAL_DAILY,    _('daily')),
    (INTERVAL_WEEKLY,   _('weekly')),
    (INTERVAL_MONTHLY,  _('monthly')),
    (INTERVAL_ANNUALLY, _('annually')),
]

INTERVAL_XAXIS = {
    INTERVAL_HOURLY:   _('hours'),
    INTERVAL_DAILY:    _('days'),
    INTERVAL_WEEKLY:   _('weeks'),
    INTERVAL_MONTHLY:  _('months'),
    INTERVAL_ANNUALLY: _('years'),
}

INTERVAL_FUNCTIONS = {
    INTERVAL_HOURLY:   signal_receivers.update_hourly,
    INTERVAL_DAILY:    signal_receivers.update_daily,
    INTERVAL_WEEKLY:   signal_receivers.update_weekly,
    INTERVAL_MONTHLY:  signal_receivers.update_monthly,
    INTERVAL_ANNUALLY: signal_receivers.update_annually,
}

class MeterType(models.Model):
    
    name = models.CharField(max_length=255,)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _(u"meter type")
        verbose_name_plural = _(u"meter types")
    
class Meter(models.Model):
    
    name = models.CharField(max_length=255,
                            help_text=_(u"Give your meter a name, for instance 'Basement meter'"))
    meter_type = models.ForeignKey(MeterType, help_text=_(u"Select a type of meter. For instance you could call all your electricity meters 'Electricity'. This looks good in the front-end!"))
    default_interval = models.ForeignKey('IntervalType', related_name='default_meter',
                                         null=True, blank=True,
                                         help_text=_(u"This is the summary that will most likely be displayed in overviews."))
    
    is_counter = models.BooleanField(default=False,
                                     verbose_name=_(u"is a counter"),
                                     help_text=_(u"Indicates that the meter is an incremental counter, ie. that every time a new number is received, the difference from the previous number should be logged. If a number is smaller than the previous, the data server assumes that counting has been reset, for instance because the Arduino has rebooted. This does not affect the counting a summarising procedure."))
    
    description = models.TextField(blank=True)
    
    def get_latest_data(self):
        data = self.meterdata_set.all().order_by('-created')
        if data:
            return data[0]

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _(u"meter")
        verbose_name_plural = _(u"meters")

class MeterData(models.Model):
    
    meter = models.ForeignKey(Meter)
    data_point = models.FloatField()
    diff = models.IntegerField(help_text=_(u"This field contains the difference (delta) from the last reading. It is used if the meter is an incremental counter. If you do not fill it out, it is filled out automatically"),
                               blank=True, null=True)
    created = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        # Set how much was incremented by...
        if not self.diff and self.meter.is_counter:
            latest = MeterData.objects.filter(meter=self.meter,
                                              data_point__lt=self.data_point).order_by('-created')
            if latest:
                self.diff = self.data_point - latest[0].data_point
            else:
                self.diff = 1
        return super(MeterData, self).save(*args, **kwargs)
    
    def __unicode__(self):
        return "Data for %s" % self.meter.name

    class Meta:
        verbose_name = _(u"data entry")
        verbose_name_plural = _(u"data entries")

class IntervalType(models.Model):

    name = models.IntegerField(choices = INTERVALS, help_text=_(u"This is the period or interval in which the summary should automatically summarise every new data entry."))
    verbose_name = models.CharField(max_length=255, help_text=_(u"You may give the interval a friendly name, otherwise an auto-generated name is used."),
                                    blank=True, null=True)

    meter_set = models.ManyToManyField(Meter, help_text=_(u"Choose multiple meters if you want this to be a summary of multiple meters. Please note that this would require the units of these meters to be the same!"), 
                                       blank=True)
    unit_name = models.CharField(max_length=255, help_text=_(u"Name the unit that's being summarised, for instance 'KWh'."))
    unit_fraction = models.FloatField(default=1, help_text=_(u"If you are doing an annual summary, you might want to use a different unit than the one from the data entries. If for instance, you are receiving KWh data, you could enter 0.001 and input 'MWh' in the 'unit name' field."))
    
    backlog = models.IntegerField(default=0, verbose_name=_(u"Backlog"),
                                  help_text=_(u"Number of days to keep old entries for. If you create a new summary and have the necessary data entries, summaries will be created until this point in time."))
    
    force_recreate = models.BooleanField(default=False,
                                         help_text=_(u"If checked, this will force a one-time recreation of all summaries based on available data entries until the point in time that is according to the backlog number of days above. If you are creating a new interval or have changed the meters included in an interval, this is quite useful! Correcting data entries does not necessitate recreating a whole interval."))
    
    def __unicode__(self):
        meters = self.meter_set.all()
        if meters:
            return _(u"%(interval)s summary for %(meters)s") % {'interval': unicode(self.get_name_display()).capitalize(), 
                                                                'meters': ", ".join([m.name for m in meters])}
        else:
            return _(u"%s summary for (no meters selected!)") % (unicode(self.get_name_display()).capitalize(),)
    
    class Meta:
        verbose_name = _(u"summary group")
        verbose_name_plural = _(u"summary groups")
        
    def save(self, *args, **kwargs):
        
        super(IntervalType, self).save(*args, **kwargs)
        
        if self.force_recreate:
            signal_receivers.create_interval_backlog(self)
            self.force_recreate = False
            self.save()

class Interval(models.Model):
    total = models.FloatField(blank=True, null=True, default=0)
    average = models.FloatField(blank=True, null=True, default=0)
    interval_type = models.ForeignKey(IntervalType)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField(editable=False)
    
    data_entries = models.IntegerField(default=0)
    
    @classmethod
    def get_to_time(cls, from_time, interval_type_id):
        """
        Get the upper bound of an interval based on its from_time and the
        type of interval. This is used to automatically set the to_time if
        unset when calling save()
        """
        from_time = from_time
        type_id = interval_type_id

        # Get the span of the readings to summarize
        if type_id == INTERVAL_HOURLY:
            to_time = from_time.replace(minute=59, second=59, microsecond=999)
        elif type_id == INTERVAL_DAILY:
            to_time = from_time.replace(hour=23, minute=59, second=59, microsecond=999)
        elif type_id == INTERVAL_WEEKLY:
            to_time = from_time + timedelta(days=6)
            to_time = to_time.replace(hour=23, minute=59, second=59, microsecond=999)
        elif type_id == INTERVAL_MONTHLY:
            __, daysofmonth = monthrange(from_time.year, from_time.month)
            to_time = from_time + timedelta(days=daysofmonth-1)
            to_time = to_time.replace(hour=23, minute=59, second=59, microsecond=999)
        elif type_id == INTERVAL_ANNUALLY:
            to_time = from_time.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999)
        
        return to_time
    
    class Meta:
        unique_together = ('interval_type', 'from_time',)
        verbose_name = _(u"summary")
        verbose_name_plural = _(u"summaries")
   
    def get_total(self):
        return "%d %s" % (self.total, self.interval_type.unit_name)
    get_total.short_description = _(u"Total")
    
    def save(self, *args, **kwargs):
        if not self.to_time:
            self.to_time = Interval.get_to_time(self.from_time, self.interval_type.name)
        return super(Interval, self).save(*args, **kwargs)
        
###########################
# SIGNAL HANDLING
###########################

post_save.connect(signal_receivers.update_hourly, sender=MeterData)
post_save.connect(signal_receivers.update_daily, sender=MeterData)
post_save.connect(signal_receivers.update_weekly, sender=MeterData)
post_save.connect(signal_receivers.update_monthly, sender=MeterData)
post_save.connect(signal_receivers.update_annually, sender=MeterData)
