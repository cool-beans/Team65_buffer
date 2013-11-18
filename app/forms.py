from django import forms
from django.db import models
from django.forms import ModelForm
from app.models import *

class ProgramCreation(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name','description']


class ProgramMod(forms.Form):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500)

