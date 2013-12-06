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
    start = forms.TimeField()
    end = forms.TimeField()

class MembershipTypeCreate(forms.ModelForm):
    class Meta:
        model = MembershipType
        fields = ['name','description','allowed_freq','visible','default_price']
class RecurringCreate(forms.Form):
    onMonday = forms.BooleanField(initial=False,required=False)
    onTuesday = forms.BooleanField(initial=False,required=False)
    onWednesday = forms.BooleanField(initial=False,required=False)
    onThursday = forms.BooleanField(initial=False,required=False)
    onFriday = forms.BooleanField(initial=False,required=False)
    onSaturday = forms.BooleanField(initial=False,required=False)
    onSunday = forms.BooleanField(initial=False,required=False)
    # Has many Events associated with one EventType
    start_date = forms.CharField(max_length=30)
    end_date = forms.CharField(max_length=30,required=False)
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=500, required=False)
    start_time = forms.CharField(max_length=30)
    end_time = forms.CharField(max_length=30)


class EventEdit(forms.Form):
    name = forms.CharField(max_length=100,required=False)
    description = forms.CharField(max_length=500, required=False)
    start_time = forms.CharField(max_length=30,required=False)
    end_time = forms.CharField(max_length=30,required=False)
