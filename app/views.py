from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

# Imports the models
from app.models import *


# Action for the default shared-todo-list/ route.
def home(request):
    context = {}
    return render(request, 'final_project/index.html', context)
