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

from pprint import pprint

@login_required
def create(request):
    # Create a new event
    user = request.user
    member = Member.objects.get(user=user)
    programs = Program.objects.all()
    context = {}
    errors = []

    if (request.method == 'GET'):
        context['user'] = user
        context['errors'] = errors
        context['programs'] = programs
        return render(request,'final_project/Events/event_create.html',context)

    elif (request.method == 'POST'):
        new_recurrence = Recurrence()
        start_date = None
        # If start date is not specified for recurring/non-recurring event,
        # return with error
        if ('start_date' not in request.POST or not request.POST['start_date']):
            errors.append('Must include start date.')
            context['user'] = user
            context['errors'] = errors
            context['programs'] = programs
            return render(request, 'final_project/Events/event_create.html', context)
        else:
            # Date is now in format YYYY-MM-DD
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
        # Store info on whether or not event recurrs/what days of the week
        isRecurring = False
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day in request.POST:
                isRecurring = True
                new_recurrence.setDayRecurrence(day, isRecurring)

        if isRecurring:
            new_recurrence.isRecurring = True

            # Look for repeating day of week closest to requested start_date
            for i in range(0, 7):
                check_date = start_date + timedelta(days=i)
                if check_date.weekday in new_recurrence.getDays():
                    start_date = check_date
                    break

            new_recurrence.start_date = start_date

        # If not recurring, just set start date to date given
        else:
            new_recurrence.start_date = start_date

        # If end date is specified and event is recurring, save it in recurrence info.
        # It's ok to not have an end date (recurrs forever)
        if (isRecurring and 'end_recurrence' in request.POST and request.POST['end_recurrence']):

            # Date is now in format YYYY-MM-DD
            end_recurrence = datetime.strptime(request.POST['end_recurrence'], '%Y-%m-%d').date()
            # If requested end date is either before the first time event
            # can recurr or before the start date: error
            if end_recurrence <= new_recurrence.start_date:
                errors.append('Invalid end date: either must be after ' \
                              'start date or after first recurrence of '\
                              'a recurring event.'  )
                context['user'] = user
                context['errors'] = errors
                context['programs'] = programs
                return render(request, 'final_project/Events/event_create.html', context)
            # If valid end date, set new_recurrence's end_recurrence
            else:
                new_recurrence.end_recurrence = request.POST['end_recurrence']

        new_recurrence.save()
        # Now Recurrence should be set, create event!
        new_eventtype = EventType(recurrence=new_recurrence)

        # For all programs, check if they are in POST,
        # if so, add them to the new EventType's programs_set
        for program in programs:
            if program.name in request.POST:
                new_eventtype.programs_set.add(program)

        eventtype_form = EventTypeCreation(request.POST, instance=new_eventtype)

        if not eventtype_form.is_valid():
            errors.append('Bad information given. Must include start date and '\
                          'event start/end time, event name, and programs associated '\
                          'with this event.')
            context['user'] = user
            context['errors'] = errors
            context['programs'] = programs
            return render(request,'final_project/Events/event_create.html', context)

        # Check if any such events/eventTypes exist already, if so, don't save form.
        if Event.getEvent(name=new_eventtype.name,
                          date=new_eventtype.recurrence.start_date,
                          start_time=new_eventtype.start_time):
            errors.append('Event with same day and start time and name already exists.')
            context['user'] = user
            context['errors'] = errors
            context['programs'] = programs
            return render(request, 'final_project/Events/event_create.html', context)

        # Save new EventType
        new_eventtype = eventtype_form.save()

        # Create new event with new EventType
        new_event = Event.eventFromType(new_eventtype)

        context['user'] = user
        context['event'] = new_event
        context['eventtype'] = new_eventtype
        return render(request,'final_project/Events/event_profile.html', context)

def profile(request):
    user = request.user
    context = {}
    errors = []

    if request.method == 'GET':
     #   errors.append('Go to schedule view page and select event to view.')
      #  context['user'] = user
       # context['errors'] = errors
        #return redirect('/final_project/events')

    #elif request.method == 'POST':
        if 'event_name' not in request.GET or not request.GET['event_name']:
            errors.append('No event name info given in GET')
        if 'event_start_date' not in request.GET or not request.GET['event_start_date']:
            errors.append('No event_start_date info given in GET')
        if 'event_start_time' not in request.GET or not request.GET['event_start_time']:
            errors.append('No event_start_time info given in GET')
        if errors:
            return redirect('/final_project/events')

        name = request.GET['event_name']

        # date is now in format "Nov. 3, 2013"
        start_date = datetime.strptime(request.GET['event_start_date'], '%b. %d, %Y').date()

        #start_time = datetime.strptime(request.GET['event_start_time'], '%I:%M %p').time()
        start_time = Event.convertTime(request.GET['event_start_time'])

        # start_time now in format HH:MM (AM|PM)
        start_time = datetime.strptime(start_time, '%I:%M %p').time()

        print "GETTING EVENT: ---------------------"
        print "\tname: " + name
        print "\tdate: " + str(start_date)
        print "\ttime: " + str(start_time)
        print "\n\n"

        # If all needed info (name, date, start_time) is there, get Event
        event = Event.getEvent(name=name, date=start_date, start_time=start_time)

        # If cannot find recurrence that matches event, redirect to events
        if not event:
            errors.append("Could not locate event, given name, start_time, date.")
            for error in errors:
                print "ERROR: " + error
                print "\tname: " + name
                print "\tdate: " + str(start_date)
                print "\ttime: " + str(start_time)

            return redirect('/final_project/events')

        context['user'] = user
        context['event'] = event
        return render(request, 'final_project/Events/event_profile.html', context)

def all(request):
    user = request.user
    context = {}
    errors = []

    today = date.today()

    # Default: set latest_date to Sunday of this week
    latest_date = Event.getSundayDate(today)

    if request.method == 'GET':
        # If navigating to page, just return view of current week.

        # If the latest_date from the last access is provided
        # along with either a button = 'prev' or 'next', calculate
        # appropriate latest_date
        if 'latest_date' in request.GET and request.GET['latest_date']:
            if 'timeframe' in request.GET and request.GET['timeframe']:
                if request.GET['timeframe'] == 'prev':
                    latest_date = request.GET['latest_date'] - timedelta(days=7)
                elif request.GET['timeframe'] == 'next':
                    latest_date = request.GET['latest_date'] + timedelta(days=7)

    events = []
    dates = []
    day_to_date = {}

    # Build list of dates in current week
    for i in range(0, 7):
        date_to_get = latest_date - timedelta(days=i)
        # Set the day of the week (0=Monday, 6=Sunday) as key to date
        day_to_date[date_to_get.weekday()] = date_to_get

        dates.append(date_to_get)

    earliest_date = latest_date - timedelta(days=6)

    # Grab all recurrences that started at least by the latest_date
    recurrences = Recurrence.objects.filter(start_date__lte=latest_date)

    for recurrence in recurrences:
        days = recurrence.getDays()
        eventtype = recurrence.eventtype
        print "Checking EventType: " + eventtype.name

        # If not a recurring event and date is within the past week, show event
        if not days and (recurrence.start_date >= earliest_date):
            day = recurrence.start_date.weekday()
            event = eventtype.event_set.filter(date=recurrence.start_date)

            # If an Event already exists for this one-time event, just append.
            if event:
                events.append(event[0])

            # Otherwise, make an Event (don't save) and append
            else:
                new_event = Event.eventFromType(eventtype)
                events.append(new_event)

        # For each day the event recurrs on, attach the event to list of events
        for day in days:
            event_date = day_to_date[day]
            print "\tevent_date: " + str(event_date)
            # If recurrence has an end_recurrence, make sure event_date is not after it!
            # Otherwise, just ignore that particular day.
            if (not recurrence.end_recurrence or
                event_date <= recurrence.end_recurrence):
                print "\tevent was appended!"
                # If event already exists,
                # append it to the proper day of the week
                event = eventtype.event_set.filter(date=event_date)
                if event:
                    events.append(event)

                # Otherwise, make an event (don't save) and append
                else:
                    new_event = Event.eventFromType(eventtype)
                    new_event.date = event_date
                    events.append(new_event)

    # Lambda function to sort the list of grumbls in place by timestamp (most recent first)
    events.sort(key=lambda event: event.date, reverse=True)

    print "***************EVENT TYPES START***************"
    for event in EventType.objects.all():
        print "name: " + event.name
        print "start_date: " + str(event.recurrence.start_date)
        print "end_recurrence: " + str(event.recurrence.end_recurrence)
        print "start_time: " + str(event.start_time)
        print "days: " + str(event.recurrence.getDays())
        print "--------------------------------------"
    print "***************EVENT TYPES END***************\n\n"

    print "***************EVENTS IN WEEK START****************"
    for e in events:
        print "EVENT: " + e.name
        print "\tdate: " + str(e.date)
        print "\tdesc: " + e.description
    print "***************EVENTS IN WEEK END****************"

    context['user'] = user
    context['latest_date'] = latest_date
    context['events'] = events
    return render(request, 'final_project/Events/events.html', context)



# If POST, expects event's original:
#  -name (string)
#  -start_date (datefield)
#  -start_time (timefield)
# Changes can include:
#  -name
#  -start_time
#  -end_time
#  -date
#  -description
#  -delete
#  -change_this_event
#  -change_following_events
@login_required
def edit(request):
    # Check if editing one-time or for all following events!
    # Given name, start_date, start_time
    # Try to getEvent() for the given info.
    # If Event does not exist:
        # error
    # If one-time change, change only event and save before return
    # If recurring change, change event and save,
    # then change EventType, save.
    # Return to event_profile of requested event

    user = request.user
    context = {}
    event = None
    errors = []

    if request.method == 'GET':
        # Check to make sure name, start_date, and start_time all included
        if 'name' not in request.GET or not request.GET['name']:
            errors.append('Missing event name.')
        if 'start_date' not in request.GET or not request.GET['start_date']:
            errors.append('Missing event start_date.')
        if 'start_time' not in request.GET or not request.GET['start_time']:
            errors.append('Missing event start_time')

        # If all are included, try to get the event requested
        if not errors:
            event = Event.getEvent(name=request.GET['name'],
                                   start_date=request.GET['start_date'],
                                   start_time=request.GET['start_time'])
            if not event:
                error = ('Could not locate event given name ({name}), ',
                         'start_date ({date}), and time ({time}).',
                         ''.format(name=request.GET['name'],
                                   date=request.GET['start_date'],
                                   time=request.GET['start_time']))
                errors.append(error)

        # If there are errors, return user to events page
        if errors:
            context['user'] = user
            context['errors'] = errors
            return redirect('final_project/events')

        # Otherwise, can assume event was located, so return event_edit
        # with event in context.
        context['user'] = user
        context['event'] = event
        return render(request, 'final_project/event_edit.html', context)

    elif request.method == 'POST':
# Check to make sure name, start_date, and start_time all included
        if 'name' not in request.POSTT or not request.POST['name']:
            errors.append('Missing event name.')
        if 'start_date' not in request.POST or not request.POST['start_date']:
            errors.append('Missing event start_date.')
        if 'start_time' not in request.POST or not request.POST['start_time']:
            errors.append('Missing event start_time')
        if ('change-once' not in request.POST and \
            'change-following' not in request.POST):
            errors.append('Missing option for change-once vs change-following')

        # If all are included, try to get the event requested
        if not errors:
            event = Event.getEvent(name=request.POST['name'],
                                   start_date=request.POST['start_date'],
                                   start_time=request.POST['start_time'])
            if not event:
                error = ('Could not locate event given name ({name}), ',
                         'start_date ({date}), and time ({time}).',
                         ''.format(name=request.POST['name'],
                                   date=request.POST['start_date'],
                                   time=request.POST['start_time']))
                errors.append(error)

        # If there are errors, return user to events page
        if errors:
            context['user'] = user
            context['errors'] = errors
            return redirect('final_project/events')

        # Otherwise, can assume event was located, so proceed to edit!

        # If one-time change,
        if 'change-series' not in request.POST:
            # Change event and save
            # Can change: name, date, start_time, end_time, description,
            #             is_cancelled
            if 'name' in request.POST and request.POST['name']:
                event.name = request.POST['name']
            if 'date' in request.POST and request.POST['date']:
                # date is now in format "Nov. 3, 2013"
                date = datetime.strptime(request.POST['date'], '%b. %d, %Y').date()
                event.date = date
            if 'start_time' in request.POST and request.POST['start_time']:
                start_time = Event.convertTime(request.POST['start_time'])
                event.start_time = start_time
            if 'end_time' in request.POST and request.POST['end_time']:
                end_time = Event.convertTime(request.POST['end_time'])
                event.start_time = end_time
            if 'description' in request.POST and request.POST['description']:
                event.description = description
            if 'is_cancelled' in request.POST:
                event.is_cancelled = True

            event.save()

        # If changing the following events as well, then change EventType, save.
        elif 'change-series' in request.POST:
            eventtype = event.eventtype
            # Change Event and Eventtype and save
            # Can change: name, date, start_time, end_time, description,
            #             is_cancelled
            if 'name' in request.POST and request.POST['name']:
                event.name = request.POST['name']
                eventtype.name = request.POST['name']
            if 'date' in request.POST and request.POST['date']:
                # date is now in format "Nov. 3, 2013"
                date = datetime.strptime(request.POST['date'], '%b. %d, %Y').date()
                event.date = date
            if 'start_time' in request.POST and request.POST['start_time']:
                start_time = Event.convertTime(request.POST['start_time'])
                event.start_time = start_time
                eventttype.start_time = start_time
            if 'end_time' in request.POST and request.POST['end_time']:
                end_time = Event.convertTime(request.POST['end_time'])
                event.start_time = end_time
                eventtype.end_time = end_time
            if 'description' in request.POST and request.POST['description']:
                event.description = description
                eventtype.description = description
            if 'is_cancelled' in request.POST:
                event.is_cancelled = True

            event.save()
            eventtype.save()

        # Return to event_profile of requested event
        context['user'] = user
        context['event'] = event
        return render(request, 'final_project/Events/event_profile.html', context)
