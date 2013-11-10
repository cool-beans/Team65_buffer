from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

# Imports the models
from app.models import *


# Action for the default shared-todo-list/ route.
def home(request):
    context = {}
    return render(request, 'final_project/index.html', context)

def programs(request):
    context = {}
    return render(request, 'final_project/programs.html', context)

def program_profile(request):
    context = {}
    return render(request, 'final_project/program_profile.html', context)

def about(request):
    context = {}
    return render(request, 'final_project/about.html', context)

def login(request):
    context = {}
    return render(request, 'final_project/login.html', context)

def register(request):
    context = {}
    return render(request, 'final_project/register.html', context)

def members(request):
    context = {}
    return render(request, 'final_project/members.html', context)

def member_profile(request):
    context = {}
    return render(request, 'final_project/member_profile.html', context)
