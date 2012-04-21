from django import forms

import models

class MeterDataForm(forms.ModelForm):
    
    created_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'datepicker',
                                                                 'data-date-format': 'yyyy-mm-dd'}),
                                   input_formats=["%Y-%m-%d"])
    created_time = forms.TimeField(initial="00:00")
    
    class Meta:
        model = models.MeterData
        exclude = ('meter', 'created')
    