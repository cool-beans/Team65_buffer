from django import forms
from django.db import models
from django.forms import ModelForm
from app.models import *

class ProgramCreation(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name','description']


class ProgramMod(forms.Form):
    name = forms.CharField(max_length=20)
    description = forms.CharField(max_length=500)

class EventTypeCreation(forms.ModelForm):
    class Meta:
        model = EventType
        fields = ['name', 'start_time', 'end_time', 'description',]

class MemberEdit(forms.Form):
    first_name = forms.CharField(max_length=100,required=False)
    last_name = forms.CharField(max_length=100,required=False)
    birthday = forms.DateField(required=False)

    phone = forms.CharField(max_length=10,required=False)
    email = forms.CharField(max_length=30,required=False)
    make_staff = forms.BooleanField(required=False)

class BookEvent(forms.Form):
    name = forms.CharField(max_length=20)
    date = forms.DateField()
    start = models.TimeField()
    end = models.TimeField()

