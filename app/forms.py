from django import forms
from django.db import models
from django.forms import ModelForm


class ProgramCreation(ModelForm):
    class Meta:
        model = Article
        fields = ['name','description']


class ProgramMod(Form):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500)

