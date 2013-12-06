from django.shortcuts import render
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


@login_required
def create(request):
    # Create a new event
    user = request.user
    member = Member.objects.get(user=user)
    programs = Program.objects.all()
    context = {}
    errors = []

    # If not staff, render events page
    if not member.staff:
        errors.append('You do not have permission to create events.')
        sunday_date = Event.getSundayDate(date.today())
        context = getContextForAll(user, errors, sunday_date)
        return render(request, 'final_project/Events/events.html', context)

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
        new_event = new_eventtype.createEvent(new_eventtype.recurrence.start_date)

        context['user'] = user
        context['event'] = new_event
        context['eventtype'] = new_eventtype
        return render(request,'final_project/Events/event_profile.html', context)

def profile(request):
    user = request.user
    context = {}
    errors = []

    if request.method == 'GET':
        name = ''
        start_date = None
        start_time = None

        # Check for valid:
        # - event_name
        # - event_start_date
        # - event_start_time

        # Check for valid event_name
        if 'event_name' not in request.GET or not request.GET['event_name']:
            errors.append('No event name info given in GET')
        else:
            name = request.GET['event_name']
        
        # Check for valid event_start_date
        if 'event_start_date' not in request.GET or not request.GET['event_start_date']:
            errors.append('No event_start_date given.')
        else:
            # date is now in format "Nov. 3, 2013"
            start_date = datetime.strptime(request.GET['event_start_date'], '%b. %d, %Y').date()
            if not start_date:
                errors.append('Invalid start_date given.')            

        # Check for valid event_start_time
        if 'event_start_time' not in request.GET or not request.GET['event_start_time']:
            errors.append('No event_start_time given.')
        else:
            # convert time into a time object
            start_time = Event.convertTime(request.GET['event_start_time'])
            if not start_time:
                errors.append('Invalid start_time given')
        
        # If errors exist, render events.html
        if errors:
            sunday_date = Event.getSundayDate(date.today())
            context = getContextForAll(user, errors, sunday_date)
            return render(request, 'final_project/Events/events.html', context)

        print "GETTING EVENT: ---------------------"
        print "\tname: " + name
        print "\tdate: " + str(start_date)
        print "\ttime: " + str(start_time)
        print "\n\n"

        # If all needed info (name, date, start_time) is there, get Event
        event = Event.getEvent(name=name, date=start_date, start_time=start_time)

        # If cannot find recurrence that matches event, render events.html
        if not event:
            errors.append("Could not locate event, given name, start_time, date.")
            sunday_date = Event.getSundayDate(date.today())
            context = getContextForAll(user, errors, sunday_date)
            return render(request, 'final_project/Events/events.html', context)


        context['user'] = user
        context['event'] = event
        return render(request, 'final_project/Events/event_profile.html', context)

def all(request):
    user = request.user
    context = {}
    errors = []

    # Default: set sunday_date to Sunday of this week
    sunday_date = Event.getSundayDate(date.today())

    if request.method == 'GET':
        # If navigating to page, just return view of current week.
        # If the sunday_date from the last access is provided
        # along with either a button = 'prev' or 'next', calculate
        # appropriate sunday_date
        if 'sunday_date' in request.GET and request.GET['sunday_date']:
            if 'timeframe' in request.GET and request.GET['timeframe']:
                if request.GET['timeframe'] == 'prev':
                    sunday_date = request.GET['sunday_date'] - timedelta(days=7)
                elif request.GET['timeframe'] == 'next':
                    sunday_date = request.GET['sunday_date'] + timedelta(days=7)

    events = []
    monday_events = []
    tuesday_events = []
    wednesday_events = []
    thursday_events = []
    friday_events = []
    saturday_events = []
    sunday_events = []

    events = Event.getEventsFromSunday(sunday_date)
    #EventType.printAllTypes()
    #Event.printEvents(events)

    context['user'] = user
    context['sunday_date'] = sunday_date
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
            sunday_date = Event.getSundayDate(date.today())
            context = getContextForAll(user, errors, sunday_date)
            return render(request, 'final_project/Events/events.html', context)

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
            sunday_date = Event.getSundayDate(date.today())
            context = getContextForAll(user, errors, sunday_date)
            return render(request, 'final_project/Events/events.html', context)

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
                event.end_time = end_time
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
