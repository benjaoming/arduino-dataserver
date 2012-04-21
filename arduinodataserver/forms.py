from django.utils.translation import ugettext as _
from django import forms

import models

class MeterDataForm(forms.ModelForm):
    
    created_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker',
                                                                 'data-date-format': 'yyyy-mm-dd'}),
                                   input_formats=["%Y-%m-%d"])
    created_time = forms.TimeField(initial="00:00")
    
    data_point = forms.FloatField(label=_(u"Data point"), help_text=_(u"Decimals allowed. For instance: 1.0 or just '1'."))
    
    class Meta:
        model = models.MeterData
        exclude = ('meter', 'created')
    