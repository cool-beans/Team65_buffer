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


def programs(request):
    programs = Program.objects.all()
    context = {'programs':programs}
    if request.user is not None:
        context['user'] = request.user
    return render(request, 'final_project/Programs/programs.html', context)

def program_profile(request,program_id):
    try:
        program = Program.objects.get(id=program_id)
        members = program.members
        context = {'user':request.user,'program':program}
        return render(request, 'final_project/Programs/program_profile.html', context)
    except Program.DoesNotExist:
        programs = Program.objects.all()
        context = {'programs':programs,'user':request.user,
                   'errors':['Error, bad program id']}
        return render(request, 'final_project/Programs/programs.html',context)


@login_required
def program_create(request):
    # Create a new program.
    user = request.user
    member = Member.objects.get(user=request.user)

    if not member.staff:
        # Make sure that the currently logged in user is a staff member
        context = {'errors':['This page requires Staff login.'],
                   'user':user,
                   'programs':Program.objects.all()}
        return render(request, 'final_project/Programs/programs.html',context)
    if (request.method == 'GET'):
        context = {'user': request.user}
        return render(request,'final_project/Programs/program_create.html',context)
    form = ProgramCreation(request.POST)
    if not form.is_valid():
        context = {'errors':['Bad name or description provided.']}
        return render(request,'final_project/Programs/program_create.html',context)
    form.save()
    program = Program.objects.get(name=form.cleaned_data['name'])
    context = {'user':request.user,
               'program':program}
    return render(request,'final_project/Programs/program_profile.html',context)


@login_required
def program_edit(request, program_id):
    # Edit an existing program.
    user = request.user
    member = Member.objects.get(user=request.user)
    program = Program.objects.get(id=program_id)
    if not member.staff:
        # Make sure that the currently logged in user is a staff member
        context = {'errors':['This page requires Staff login.'],
                   'user':user,
                   'programs':Program.objects.all()}
        return render(request, 'final_project/Programs/programs.html',context)
    if (request.method == 'GET'):
        context = {'user':request.user}
        return render(request, 'final_project/Programs/program_edit.html',context)
    form = ProgramMod(request.POST)
    if not form.is_valid():
        context = {'user':request.user,'errors':['Bad name or description provided.']}
        return render(request,'final_project/Programs/program_edit.html',context)
    if (form.cleaned_data['name']):
        program.name = form.cleaned_data['name']
    if (form.cleaned_data['description']):
        program.description = form.cleaned_data['description']
    program.save()
    context = {'user':request.user,
               'program':program}
    return render(request,'final_project/Programs/program_profile.html',context)


