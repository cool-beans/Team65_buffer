from django.shortcuts import render,redirect
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from datetime import *

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from app.forms import *
# Imports the models
from app.models import *

from events_helper_functions import getContextForAll

from pprint import pprint
from app.forms import *


# A Helper method to pad out the days and transpose them to the right place.
def getdays(monday):
    days = [list(Event.objects.filter(date__exact=monday).order_by('start_time','end_time')),
            list(Event.objects.filter(date__exact=monday + timedelta(1)).order_by('start_time','end_time')),
            list(Event.objects.filter(date__exact=monday + timedelta(2)).order_by('start_time','end_time')),
            list(Event.objects.filter(date__exact=monday + timedelta(3)).order_by('start_time','end_time')),
            list(Event.objects.filter(date__exact=monday + timedelta(4)).order_by('start_time','end_time')),
            list(Event.objects.filter(date__exact=monday + timedelta(5)).order_by('start_time','end_time')),
            list(Event.objects.filter(date__exact=monday + timedelta(6)).order_by('start_time','end_time'))]
    most_days = len(days[0])
    # Find the day with the greatest length.
    for day in days:
        l = len(day)
        if l > most_days:
            most_days = l
    padded_days = [(day + [None]*(most_days-len(day))) for day in days]
    transposed = map(list,zip(*padded_days))
    return transposed



@login_required
def create_recurring(request):
    member = request.user.member
    context = {'user':request.user,'member':member}

    # The user must be staff.
    if not member.staff:
        context['errors'] = ['Error: Only staff members can create events.']
        monday = date.today() + timedelta(-date.today().weekday())
        context['monday'] = str(monday)
        context['days'] = getdays(monday)
        return render(request, 'final_project/Events/events.html', context)


    # Get and sanitize all the fields.
    form = RecurringCreate(request.POST)

    if not form.is_valid():
        context['errors'] = ['Error: Bad form data.']
        return render(request, 'final_project/Events/create_recurring.html',context)


    start_time=form.cleaned_data['start_time']
    end_time=form.cleaned_data['end_time']
    start_date = datetime.strptime(form.cleaned_data['start_date'],"%Y-%m-%d")
    end_date = datetime.strptime(form.cleaned_data['end_date'],"%Y-%m-%d")
    default_start_time=time(hour=int(start_time[0:2]),minute=int(start_time[3:5]))
    default_end_time=time(hour=int(end_time[0:2]),minute=int(end_time[3:5]))
    rec = RecurringEvent(onMonday=form.cleaned_data['onMonday'],
                         onTuesday=form.cleaned_data['onTuesday'],
                         onWednesday=form.cleaned_data['onWednesday'],
                         onThursday=form.cleaned_data['onThursday'],
                         onFriday=form.cleaned_data['onFriday'],
                         onSaturday=form.cleaned_data['onSaturday'],
                         onSunday=form.cleaned_data['onSunday'],
                         name=form.cleaned_data['name'],
                         description=form.cleaned_data['description'],
                         start_date=start_date,
                         end_date=end_date,
                         default_start_time=default_start_time,
                         default_end_time=default_end_time)




    # Spawn all of the events associated.
    rec.save()
    rec.spawn_events()

    # Give the context the most recent monday.

    monday = date.today() + timedelta(-date.today().weekday())
    context['monday'] = str(monday)
    context['days'] = getdays(monday)

    return render(request,'final_project/Events/events.html',context)

def profile(request,event_id):
    context = {}
    if request.user.is_authenticated():
        context['user'] = request.user
        context['member'] = request.user.member
        member = request.user.member
    try:
        event = Event.objects.get(id__exact=event_id)
    except Event.DoesNotExist:
        context['errors'] = ['Error: No such event.']
        monday = date.today() + timedelta(-date.today().weekday())
        context['monday'] = str(monday)
        context['days'] = getdays(monday)
        return render(request,'final_project/Events/events.html',context)
    context['event'] = event
    if len(event.booked.filter(id__exact=member.id)) == 0 and \
            len(event.attended.filter(id__exact=member.id)) == 0:
        context['book'] = True
    if len(event.booked.filter(id__exact=member.id)) > 0:
        context['attendcancel'] = True

    return render(request,'final_project/Events/event_profile.html',context)

@login_required
def book(request,event_id):
    member = request.user.member
    context = {'user':request.user,'member':member}
    try:
        event = Event.objects.get(id__exact=event_id)
    except Event.DoesNotExist:
        context['errors'] = ['Error: No such event.']
        monday = date.today() + timedelta(-date.today().weekday())
        context['monday'] = str(monday)
        context['days'] = getdays(monday)
        return render(request,'final_project/Events/events.html',context)
    event.booked.add(member)
    event.save()
    context['event'] = event
    context['alert'] = ['Successfully Booked.']
    return redirect('/final_project/event_profile/'+ event_id,context)

@login_required
def attend(request,event_id):
    member = request.user.member
    context = {'user':request.user,'member':member}
    try:
        event = Event.objects.get(id__exact=event_id)
    except Event.DoesNotExist:
        context['errors'] = ['Error: No such event.']
        monday = date.today() + timedelta(-date.today().weekday())
        context['monday'] = str(monday)
        context['days'] = getdays(monday)
        return render(request,'final_project/Events/events.html',context)
    event.booked.remove(member)
    event.cancelled.remove(member)
    event.attended.add(member)
    event.save()
    context['event'] = event
    context['alert'] = ['Successfully Attended.']
    return redirect('/final_project/event_profile/'+ event_id,context)


@login_required
def cancel(request,event_id):
    member = request.user.member
    context = {'user':request.user,'member':member}
    try:
        event = Event.objects.get(id__exact=event_id)
    except Event.DoesNotExist:
        context['errors'] = ['Error: No such event.']
        monday = date.today() + timedelta(-date.today().weekday())
        context['monday'] = str(monday)
        context['days'] = getdays(monday)
        return render(request,'final_project/Events/events.html',context)
    event.cancelled.add(member)
    event.booked.remove(member)
    event.attended.remove(member)
    event.save()
    context['event'] = event
    context['alert'] = ['Successfully Cancelled.']
    return redirect('/final_project/event_profile/'+ event_id,context)



def create(request):
    return None

def edit(request,event_id):
    member = request.user.member
    context = {'user':request.user,'member':member}

    # The user must be staff.
    if not member.staff:
        context['errors'] = ['Error: Only staff members can create events.']
        return render(request, 'final_project/Events/events.html', context)

    try:
        event = Event.objects.get(id__exact=event_id)
    except Event.DoesNotExist:
        context['errors'] = ['Error: No such event.']
        monday = date.today() + timedelta(-date.today().weekday())
        context['monday'] = str(monday)
        context['days'] = getdays(monday)
        return render(request,'final_project/Events/events.html',context)

    if request.method == 'GET':
        context['event'] = event
        return render(request, 'final_project/Events/event_edit.html',context)
    form = EventEdit(request.POST)

    if not form.is_valid():
        context['errors'] = ['Error: Bad form data.']
        monday = date.today() + timedelta(-date.today().weekday())
        context['monday'] = str(monday)
        context['days'] = getdays(monday)
        return render(request, 'final_project/Events/event_edit.html',context)

    start_time=form.cleaned_data['start_time']
    end_time=form.cleaned_data['end_time']

    changed = False
    if start_time:
        event.start_time=time(hour=int(start_time[0:2]),minute=int(start_time[3:5]))
        changed = True
    if end_time:
        event.end_time=time(hour=int(end_time[0:2]),minute=int(end_time[3:5]))
        changed = True
    if form.cleaned_data['name'] != '':
        event.name = form.cleaned_data['name']
        changed = True
    if form.cleaned_data['description'] != '':
        event.description = form.cleaned_data['description']
        changed = True
    if changed:
        if not event.description: event.description = event.recurrence.description
        if not event.name: event.name = event.recurrence.name
        event.recurrence = None
    event.save()
    context['event'] = event
    return redirect('/final_project/event_profile/'+ event_id)

def backweek(request,prev_monday):
    context = {}
    if request.user.is_authenticated():
        context['user'] = request.user
        context['member'] = request.user.member
    monday = datetime.strptime(prev_monday,"%Y-%m-%d") - timedelta(7)
    context['monday'] = str(monday.date())
    context['days'] = getdays(monday)
    return render(request,'final_project/Events/events.html',context)

def forwardweek(request,next_monday):
    context = {}
    if request.user.is_authenticated():
        context['user'] = request.user
        context['member'] = request.user.member
    monday = datetime.strptime(next_monday,"%Y-%m-%d") + timedelta(7)
    context['monday'] = str(monday.date())
    context['days'] = getdays(monday)
    return render(request,'final_project/Events/events.html',context)


def all(request):
    context = {}
    if request.user.is_authenticated():
        context['user'] = request.user
        context['member'] = request.user.member
    monday = date.today() + timedelta(-date.today().weekday())
    if request.method == "POST" and  'monday' in request.POST and \
            request.POST['monday']:
        monday = request.POST['monday'] + timedelta(-request.POST['monday'].weekday())

    context['monday'] = str(monday)
    context['days'] = getdays(monday)
    return render(request,'final_project/Events/events.html',context)
