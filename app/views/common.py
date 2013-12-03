from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import *#datetime, date, timedelta

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from app.forms import *
# Imports the models
from app.models import *

# Action for the default shared-todo-list/ route.
def home(request):
    context = {}
    if request.user is not None:
        context['user'] = request.user
    return render(request, 'final_project/Common/index.html', context)



def about(request):
    context = {}
    if request.user is not None:
        context['user'] = request.user
    return render(request, 'final_project/Common/about.html', context)
