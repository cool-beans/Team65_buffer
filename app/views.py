from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
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
    return render(request, 'final_project/index.html', context)

def programs(request):
    programs = Program.objects.all()
    context = {'programs':programs}
    if request.user is not None:
        context['user'] = request.user
    return render(request, 'final_project/programs.html', context)

def program_profile(request,program_id):
    try:
        program = Program.objects.get(id=program_id)
        members = program.members
        context = {'user':request.user,'program':program}
        return render(request, 'final_project/program_profile.html', context)
    except Program.DoesNotExist:
        programs = Program.objects.all()
        context = {'programs':programs,'user':request.user,
                   'errors':['Error, bad program id']}
        return render(request, 'final_project/programs.html',context)


def about(request):
    context = {}
    if request.user is not None:
        context['user'] = request.user
    return render(request, 'final_project/about.html', context)

#def login(request):
#    context = {}
#    return render(request, 'final_project/login.html', context)

def register(request):
    context = {}
    errors = []

    # If simply requesting the register page
    if request.method == 'GET':
        context['errors'] = errors
        return render(request, 'final_project/register.html', context)

    # If trying to register
    elif request.method == 'POST':
        # Gigantic if statement checking if form is valid and fields are
        # not blank
        if not 'username' in request.POST or not request.POST['username']\
            or not 'pass1' in request.POST or not request.POST['pass1']\
            or not 'pass2' in request.POST or not request.POST['pass2']\
            or not 'first_name' in request.POST or not request.POST['first_name']\
            or not 'last_name' in request.POST or not request.POST['last_name']\
            or not 'birthday' in request.POST or not request.POST['birthday']\
            or not 'phone' in request.POST or not request.POST['phone']\
            or not 'email' in request.POST or not request.POST['email']:

            errors.append('Missing a field.')

        # Check to make sure username was unique
        elif len(User.objects.filter(username=request.POST['username'])) > 0:
            errors.append('Username is already taken.')

        # Check to make sure passwords match
        elif request.POST['pass1'] != request.POST['pass2']:
            errors.append('Passwords do not match.')

        # Check to make sure phone is 10 digits
        elif len(request.POST['phone']) != 10:
            errors.append('Phone must be 10 digits.')

        # Data was all clean, can create and save new user and member
        else:
            # create a new user and save it
            new_user = User.objects.create_user(username=request.POST['username'], \
                                        password=request.POST['pass1'], \
                                        email=request.POST['email'])
            new_user.save()
            new_user_id = new_user.id
            context['user'] =  new_user
            #membership = Membership(name="Blah",allowed_feq=1,price=100.00)

            # Create a new member and associate it with the new user
            new_member = Member(user=new_user,\
                                first_name=request.POST['first_name'],\
                                last_name=request.POST['last_name'],\
                                birthday=request.POST['birthday'],\
                                phone=request.POST['phone'],\
                                email=request.POST['email'],\
                                creation_date=datetime.now(),\
                                )
            new_member.save()
            # Logs in new user and redirects to their member_profile page
            new_user = authenticate(username=request.POST['username'], \
                                    password=request.POST['pass1'])
            login(request, new_user)

            return redirect('/final_project/member_profile/' + str(new_user_id))

    context['errors'] = errors
    return render(request, 'final_project/register.html', context)

@login_required
def members(request):
    context = {}
    context['user'] = request.user
    context['members'] = Member.objects.all()
    context['programs'] = Program.objects.all()
    return render(request, 'final_project/members.html', context)

@login_required
def filter_members (request, program_id):
    context = {}
    user = request.user
    members = []
    try:
        program = Program.objects.get(id=program_id)
        members = Member.objects.filter(program=program).order_by('first_name')
    except Program.DoesNotExist:
        members = Member.objects.all()


    context['user'] = user
    context['members'] = members
    context['programs'] = Program.objects.all()
    return render(request, 'final_project/members.html', context)



#TODO: make member_profile not accessible except by staff and the member themselves.
@login_required
def member_profile(request, member_id):
    context = {}
    user = request.user
    member = Member.objects.get(user=user)

    print "IN MEMBER_PROFILE!"
    print user.username + "'s member_id: " + str(user.member.id)
    print "Is trying to access member_id: " + str(member_id)


    # Are they staff? If so then let them see whoever
    if member.staff:
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            member = Member.objects.get(user=user)
    # They are not staff. Only let them see their own profile.
    else:
        member = Member.objects.get(user=request.user)

    in_program = [ prog for prog in Program.objects.all() \
                       if len(prog.members.filter(id=member.id)) != 0]

    context['user'] = user
    context['member'] = member
    context['programs'] = in_program
    return render(request, 'final_project/member_profile.html', context)

# member_edit(request, member_id)
#
# Only Staff can get access to this for profiles besides their own
# The only the following can be edited:
#	- password
#	- first_name
#	- last_name
#	- birthday
#	- phone
#	- email



@login_required
def member_edit(request, member_id):
    context = {}
    user = request.user
    member = Member.objects.get(id=member_id)
    errors = []
    # If simply getting the page to edit
    if request.method == 'GET':
        in_program = [ prog for prog in Program.objects.all() \
                              if len(prog.members.filter(id=member.id)) != 0]
        not_in_program = [ prog for prog in Program.objects.all() \
                              if len(prog.members.filter(id=member.id)) == 0]
        print not_in_program

        context['in_program'] = in_program
        context['not_in_program'] = not_in_program


    # If trying to save changes to member
    elif request.method == 'POST':
        # Gigantic if statement checking if form is valid and fields are
        # not blank

        # Data was all clean, can modify and save old_user and old_member
        # Then redirect to member_profile.html
        form = MemberEdit(request.POST)

        if not form.is_valid():
            errors.append('Error, bad form data')
            context = {'user':user,'member':member,
                       'errors':errors}
            return render(request,'final_project/member_edit.html',context)
        else:
            old_member = Member.objects.get(id=member_id)
            old_user = old_member.user

            # Change first_name, last_name, birthday, phone, and email
            # of the old_member and save the old_member
            if form.cleaned_data['first_name'] is not None:
                old_member.first_name = request.POST['first_name']
            if form.cleaned_data['last_name'] is not None:
                old_member.last_name = request.POST['last_name']
            if form.cleaned_data['birthday'] is not None:
                old_member.birthday = request.POST['birthday']
            if form.cleaned_data['phone'] is not None:
                old_member.phone = request.POST['phone']
            if form.cleaned_data['email'] is not None:
                old_member.email = request.POST['email']
            old_member.save()
            context['user'] = user
            context['member'] = old_member
            context['errors'] = errors
            print "CHECKING THROUGH ADD"
            for prog in Program.objects.all():
                name = prog.name
                print name
                if name in request.POST and request.POST[name]:
                    print "IT IS HERE"
                    print request.POST[name]
                    if request.POST[name] == 'remove':
                        prog.members.remove(member)
                    elif request.POST[name] == 'add':
                        print "ADD", request.POST[name]
                        prog.members.add(member)
                    prog.save()

            return redirect('/final_project/member_profile/' + member_id)

    context['user'] = user
    context['member'] = member
    context['errors'] = errors
    return render(request, 'final_project/member_edit.html', context)


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
        return render(request, 'final_project/programs.html',context)
    if (request.method == 'GET'):
        context = {'user': request.user}
        return render(request,'final_project/program_create.html',context)
    form = ProgramCreation(request.POST)
    if not form.is_valid():
        context = {'errors':['Bad name or description provided.']}
        return render(request,'final_project/program_create.html',context)
    form.save()
    program = Program.objects.get(name=form.cleaned_data['name'])
    context = {'user':request.user,
               'program':program}
    return render(request,'final_project/program_profile.html',context)


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
        return render(request, 'final_project/programs.html',context)
    if (request.method == 'GET'):
        context = {'user':request.user}
        return render(request, 'final_project/program_edit.html',context)
    form = ProgramMod(request.POST)
    if not form.is_valid():
        context = {'user':request.user,'errors':['Bad name or description provided.']}
        return render(request,'final_project/program_edit.html',context)
    if (form.cleaned_data['name']):
        program.name = form.cleaned_data['name']
    if (form.cleaned_data['description']):
        program.description = form.cleaned_data['description']
    program.save()
    context = {'user':request.user,
               'program':program}
    return render(request,'final_project/program_profile.html',context)

@login_required
def event_create(request):
    # Create a new event
    user = request.user
    member = Member.objects.get(user=user)
    context = []
    errors = []

    if (request.method == 'GET'):
        context['user'] = user
        context['errors'] = errors
        return render(request,'final_project/event_create.html',context)

    elif (request.method == 'POST'):
        new_recurrence = Recurrence()
        isRecurring = False
        for day in range(0, 7):
            if str(day) in request.POST and request.POST[str(day)]:
                isRecurring = True
                new_recurrence.setDayRecurrence(day, isRecurring)

        if isRecurring:
            new_recurrence.isRecurring = True

        # If start date is not specified for recurring/non-recurring event,
        # return with error
        if ('start_date' not in request.POST or not request.POST['start_date']):
            errors.append('Must include start date.')
            context['user'] = user
            context['errors'] = errors
            return render(request, 'final_project/event_create.html', context)
        else:
            new_recurrence.start_date = request.POST['start_date']

        # If end date is specified, save it in recurrence info.
        # It's ok to not have an end date (recurrs forever)
        if ('end_date' in request.POST and request.POST['end_date']):
            new_recurrence.end_date = request.POST['end_date']

        # Now Recurrence should be set, create event!
        new_eventtype = EventType(recurrence=new_recurrence)
        eventtype_form = EventTypeCreation(request.POST, instance=new_eventtype)

        if not eventtype_form.is_valid():
            errors.append('Bad information given. Must include start and '\
                          'end date, event name, and programs associated '\
                          'with this event.')
            context['user'] = user
            context['errors'] = errors
            return render(request,'final_project/event_create.html', context)

        # Check if any such events exist already, if so, don't save form.
        # Don't want to save when:
        # - there already exists an Event that has the same name and start_time and
        #   is in between the start_date and end_date
        # - overlaps with another EventType that has the same start_time and name
        if Event.getEvent(name=name, date=date, start_time=start_time):
            errors.append('Event with same day and start time and name already exists.')
            context['user'] = user
            context['errors'] = errors
            return render(request, 'final_project/event_create.html', context)

        # Create new event with
        new_event = Event(name=new_eventtype.name,
                          date=new_eventtype.recurrence.start_date,
                          start_time=new_eventtype.start_time,
                          end_time=new_eventtype.end_time,
                          note=new_eventtype.note,
                          event_type = new_eventtype)

        new_eventtype = eventtype_form.save()

        # Just create the event to display, no need to actually save it yet.
        #new_event.save()

        context['user'] = user
        context['event'] = new_event
        context['eventtype'] = new_eventtype
        return render(request,'final_project/event_profile.html', context)

def event_profile(request):
    user = request.user
    context = []
    errors = []

    if request.method == 'GET':
        errors.append('Go to schedule view page and select event to view.')
        context['user'] = user
        context['errors'] = errors
        return redirect('final_project/events')

    elif request.method == 'POST':
        if 'name' not in request.POST or not request.POST['name']:
            errors.append('No event name info given in POST')
        if 'date' not in request.POST or not request.POST['date']:
            errors.append('No event date info given in POST')
        if 'start_time' not in request.POST or not request.POST['start_time']:
            errors.append('No event start_time info given in POST')
        if errors:
            return redirect('final_project/events')

        eventtypes = EventType.objects.filter(name=name).filter(start_time=start_time)
        event = None
        date = request.POST['date']
        for eventtype in eventtypes:
            # If the event started before or on date
            if eventtype.recurrence.start_date <= date:
                weekday = date.weekday
                # If event's weekday was in eventtype's weekdays
                if weekday in eventtype.recurrence.getDays():
                    found_event = eventtype.event_set.filter(date=request.POST['date'])
                    # If eventtype already had an event that exactly matched, set event
                    if found_event:
                        event = found_event
                        break
                    # Otherwise, create an event
                    else:
                        event = Event(name=new_eventtype.name,
                          date=new_eventtype.recurrence.start_date,
                          start_time=new_eventtype.start_time,
                          end_time=new_eventtype.end_time,
                          note=new_eventtype.note,
                          event_type = new_eventtype)
                        break

        # If cannot find recurrence that matches event, redirect to events
        if not event:
            errors.append("Could not locate event, given name, start_time, date.")
            return redirect('final_project/events')

        context['user'] = user
        context['event'] = event
        return render(request, 'final_project/event_profile.html', context)

@login_required
def events(request):
    user = request.user
    context = {}
    errors = []

    # Default: set latest_date to today
    latest_date = date.today()
    if request.method == 'GET':
        # If navigating to page, just return view of current week.
        pass

    elif request.method == 'POST':
        # If the latest_date from the last access is provided
        # along with either a button = 'prev' or 'next', calculate
        # appropriate latest_date
        if 'latest_date' in request.POST and request.POST['latest_date']:
            if 'button' in request.POST and request.POST['button']:
                if request.POST['button'] == 'prev':
                    latest_date = date.today() - timedelta(days=7)
                elif request.POST['button'] == 'next':
                    latest_date = date.today() + timedelta(days=7)

    events = []
    dates = []
    day_to_date = {}
    events_on_days = {}

    # Build list of dates in current week
    for i in range(0, 7):
        date_to_get = latest_date - timedelta(days=i)
        # Set the day of the week (0=Monday, 6=Sunday) as key to date
        day_to_date[date_to_get.weekday()] = date_to_get

        dates.append(date_to_get)

        # Initialize each day of the week to an empty list
        events_on_days[i] = []

    # Grab all recurrences that started at least a week ago
    recurrences = Recurrence.objects.filter(start_date__lte=dates[6])

    for recurrence in recurrences:
        for day in recurrence.getDays():
            event_date = day_to_date[day]
            eventtype = recurrence.eventtype

            # If event already exists,
            # append it to the proper day of the week
            event = eventtype.event_set.filter(date=event_date)
            if event:
                events_on_days[day].append(event)

            # Otherwise, make an event (don't save) and append
            else:
                new_event = Event(name=new_eventtype.name,
                          date=new_eventtype.recurrence.start_date,
                          start_time=new_eventtype.start_time,
                          end_time=new_eventtype.end_time,
                          note=new_eventtype.note,
                          event_type = new_eventtype)
                events_on_days[day].append(event)

    context['user'] = user
    context['latest_date'] = latest_date
    return render(request, 'final_project/events.html', context)



# If POST, expects event's original:
#  -name (string)
#  -start_time (timefield)
#  -end_time (timefield)
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
def event_edit(request):
    # Check if editing one-time or for all following events!
    user = request.user
    context = []
    errors = []

    if request.method == 'GET':
        context['user'] = user
        return render(request, 'final_project/event_edit.html', context)

    elif request.method == 'POST':
        return render(request, 'final_project/event_edit.html', context)
        # If name, start_time, and date are there
        # If event already exists, just change the fields that are not None and save
        context['user'] = user
        return render(request, 'final_project/event_edit.html', context)

        # If event does not exist, make sure all fields are there.

