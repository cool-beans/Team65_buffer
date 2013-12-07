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
from django.core.mail import send_mail


@login_required
def all(request):
    member = request.user.member
    context = {'user':request.user,'member':member}
    context['programs'] = Program.objects.all()
    context['total_members'] = Member.objects.count()
    return render(request,'final_project/Emails/emails.html',context)


@login_required
def send(request):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member,'programs':Program.objects.all()}
    if not member.staff:
        context['errors'] = ['Error: This page requires staff login.']
        return render(request,'final_project/index.html',context)

    if not 'content' in request.POST or not request.POST['content']:
        context['errors'] = ['Error: Could not find an email to send.']
        return render(request,'final_project/Emails/emails.html',context)
    if not 'subject' in request.POST or not request.POST['subject']:
        context['errors'] = ['Error: Could not find a subject.']
        return render(request,'final_project/Emails/emails.html',context)

    content = request.POST['content']
    subject = request.POST['subject']


    recipients = []
    if 'all' in request.POST and request.POST['all']:
        recipients = Member.objects.all()
    else:
        for program in Program.objects.all():
            name = program.name
            if name in request.POST and request.POST[name]:
                for member in program.members.all():
                    if not member in recipients:
                        recipients.append(member)
        for member in Member.objects.all():
            name = member.user.username
            if name in request.POST and request.POST[name]:
                if not member in recipients:
                    recipients.append
    if len(recipients) == 0:
        context['errors'] = ['Error: You must select at least one program to email to.']
        return render(request,'final_project/Emails/emails.html',context)

    context['alert'] = "Email successfully sent to: "
    for member in recipients:
        replsubj = subject.replace("{firstname}",member.first_name).replace("{lastname}",member.last_name)
        email = content.replace("{firstname}",member.first_name).replace("{lastname}",member.last_name)
        send_mail(subject=replsubj,
                  message=email,
                  from_email="admin@teambusiness.com",
                  recipient_list = [member.email])
        context['alert'] += member.name()
    return render(request,'final_project/Emails/emails.html',context)



