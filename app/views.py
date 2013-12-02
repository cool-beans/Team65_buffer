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
            if 'make_staff' in request.POST and member.staff:
                old_member.staff = True
            old_member.save()
            context['user'] = user
            context['member'] = old_member
            context['errors'] = errors
            for prog in Program.objects.all():
                name = prog.name
                if name in request.POST and request.POST[name]:
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
    programs = Program.objects.all()
    context = {}
    errors = []

    if (request.method == 'GET'):
        context['user'] = user
        context['errors'] = errors
        context['programs'] = programs
        return render(request,'final_project/event_create.html',context)

    elif (request.method == 'POST'):
        new_recurrence = Recurrence()
        isRecurring = False
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            if day in request.POST:
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
            context['programs'] = programs
            return render(request, 'final_project/event_create.html', context)

        new_recurrence.start_date = request.POST['start_date']

        # If end date is specified, save it in recurrence info.
        # It's ok to not have an end date (recurrs forever)
        if ('end_date' in request.POST and request.POST['end_date']):
            new_recurrence.end_recurrence = request.POST['end_date']

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
            return render(request,'final_project/event_create.html', context)

        # Check if any such events/eventTypes exist already, if so, don't save form.
        if Event.getEvent(name=new_eventtype.name,
                          date=new_eventtype.recurrence.start_date,
                          start_time=new_eventtype.start_time):
            errors.append('Event with same day and start time and name already exists.')
            context['user'] = user
            context['errors'] = errors
            context['programs'] = programs
            return render(request, 'final_project/event_create.html', context)

        # Create new event with
        new_event = Event(name=new_eventtype.name,
                          date=new_eventtype.recurrence.start_date,
                          start_time=new_eventtype.start_time,
                          end_time=new_eventtype.end_time,
                          description=new_eventtype.description,
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
        start_time = request.GET['event_start_time']
        # If all needed info (name, date, start_time) is there, get Event
        event = Event.getEvent(name=name, date=start_date, start_time=start_time)

        # If cannot find recurrence that matches event, redirect to events
        if not event:
            errors.append("Could not locate event, given name, start_time, date.")
            return redirect('/final_project/events')

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
    recurrences = recurrences.filter(Q(end_recurrence__gte=latest_date) | Q(end_recurrence__isnull=True))

    for recurrence in recurrences:
        days = recurrence.getDays()
        eventtype = recurrence.eventtype

        # If no recurring days and date is
        if not days and (recurrence.start_date >= earliest_date):
            day = recurrence.start_date.weekday()
            event = eventtype.event_set.filter(date=recurrence.start_date)

            # If an Event already exists for this one-time event, just append.
            if event:
                events.append(event)

            # Otherwise, make an Event (don't save) and append
            else:
                new_event = Event(name=eventtype.name,
                          date=eventtype.recurrence.start_date,
                          start_time=eventtype.start_time,
                          end_time=eventtype.end_time,
                          description=eventtype.description,
                          event_type = eventtype)
                events.append(new_event)

        for day in days:
            event_date = day_to_date[day]

            # If event already exists,
            # append it to the proper day of the week
            event = eventtype.event_set.filter(date=event_date)
            if event:
                events.append(event)

            # Otherwise, make an event (don't save) and append
            else:
                new_event = Event(name=eventtype.name,
                          date=eventtype.recurrence.start_date,
                          start_time=eventtype.start_time,
                          end_time=eventtype.end_time,
                          description=eventtype.description,
                          event_type = eventtype)
                events.append(new_event)

    # Lambda function to sort the list of grumbls in place by timestamp (most recent first)
    events.sort(key=lambda event: event.date, reverse=True)
    context['user'] = user
    context['latest_date'] = latest_date
    context['events'] = events
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
    context = {}
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


@login_required
def book_event(request):
    user = request.user
    member = Member.objects.get(user=request.user)
    context = {'user':user,'member':member}
    if (request.method == 'GET'):
        return render(request,'final_project/book_event.html',context)

    form = BookEvent(request.POST)
    if not form.is_valid():
        context['errors'] = ['Error, bad form data.']
        return render(request,'final_project/book_event.html',context)

    e_type = EventType.objects.get(name=form.cleaned_data['type'])
    event = Event.objects.get_or_create(name=form.cleaned_data['name'],
                                        date=form.cleaned_data['date'],
                                        start=form.cleaned_data['start'],
                                        end=form.cleaned_data['end'],
                                        event_type=e_type)
    event.attendees.add(member)
    event.save()
    context['event'] = event
    return render(request,'final_project/event_profile.html',context)


@login_required
def create_membership(request):
    user = request.user
    member = Member.objects.get(user=request.user)
    context = {'user':user,'member':member}

    # Sanitize the data.
    if request.method == 'GET':
        return render(request, 'final_project/buy_membership.html',context)
    if not 'membership' in request.POST or not request.POST['membership']:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/buy_membership.html',context)
    try:
        mem_type = MembershipType.get(name=request.POST['name'])
    except MembershipType.DoesNotExist:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/buy_membership.html',context)

    # If there is no price specified just use the default price.
    if not 'price' in request.POST or not request.POST['price']:
        price = mem_type.default_price
    else: price = request.POST['price']

    # Create a new membership.
    membership = Membership(price=price,mem_type=mem_type)
    if 'exp_date' in request.POST and request.POST['exp_date']:
        membership.exp_date = request.POST['exp_date']
    membership.save()
    member.membership = membership
    member.save()

    return render(request,'final_project/receipt.html', context)

@login_required
def view_membership(request,membership_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Try to get the membership.
    try:
        mem = Membership.objects.get(id__exact=membership_id)
    except Membership.DoesNotExist:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/member_profile.html',context)
    # Either they are staff or they need to own that particular membership
    if member.memberships.filter(id__exact=membership_id).count() == 0 and \
            not member.staff:
        context['errors'] = ['Error: You do not have access to that membership.']
        return render(request, 'final_project/member_profile.html',context)
    context['membership'] = mem
    return render(request,'final_project/membership_view.html',context)

@login_required
def cancel_membership(request,membership_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Try to get the membership.
    try:
        mem = Membership.objects.get(id__exact=membership_id)
    except Membership.DoesNotExist:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/member_profile.html',context)
    # Either they are staff or they need to own that particular membership
    if member.memberships.filter(id__exact=membership_id).count() == 0 and \
            not member.staff:
        context['errors'] = ['Error: You do not have access to that membership.']
        return render(request, 'final_project/member_profile.html',context)

    # Cancel the membership.
    mem.cancelled = True
    mem.cancelled_date = datetime.now()
    mem.save()
    return render(request,'final_project/member_profile.html',context)

def memberships(request):
    context = {}
    if request.user is not None:
        context['user'] = request.user
        context['member'] = Member.objects.get(user=request.user)
    context['memberships'] = MembershipType.objects.all()
    return render(request,'final_projects/memberships.html',context)

@login_required
def create_membershiptype(request):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    if not member.staff:
        context['errors'] = ['Error: This page requires staff login.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/memberships.html',context)
    form = MembershipTypeCreation(request.POST)
    if not form.is_valid():
        context['errors'] = ['Error: Bad membership data']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/memberships.html',context)
    form.save()
    m_type = MembershipType.objects.get(name=form.cleaned_data['name'])
    context['membershipType'] = m_type
    return render(request,'final_projects/membershiptype_view.html',context)

@login_required
def view_membershiptype(request):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Does the membership exist?
    if not mem_type in request.POST or not request.POST['mem_type']:
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/memberships.html',context)
    try:
        mem_type = MembershipType.get(name=request.POST['mem_type'])
        context['membership_type'] = mem_type
    except MembershipType.DoesNotExist:
        context['errors'] = ['Error: No such membership']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/memberships.html',context)
    return render(request,'final_project/view_membershiptype.html',context)

@login_required
def edit_memberhiptype(request,membership_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    if not member.staff:
        context['errors'] = ['Error: That page requires staff access.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/memberships.html',context)


    # Try to get the membership.
    try:
        mem_type = MembershipType.objects.get(id__exact=membership_id)
    except MembershipType.DoesNotExist:
        context['errors'] = ['Error: Could not find membership to edit.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/memberships.html',context)
    if 'name' in request.POST and request.POST['name']:
        mem_type.name = request.POST['name']
    if 'description' in request.POST and request.POST['description']:
        mem_type.description = request.POST['description']
    if 'default_price' in request.POST and request.POST['default_price']:
        mem_type.default_price = request.POST['default_price']
    mem_type.save()
    context['membership_type'] = mem_type
    return render(request,'final_project/view_membershiptype.html', context)



@login_required
def cost_analysis(request):
    user = request.user
    member = Member.objects.get(user=request.user)
    context = {'user':user,'member':member}
    if not member.staff:
        context['errors'] = ['Error: That page requires staff access.']
        return render(request,'final_project/programs.html',context)

    cost = {}
    for program in Program.objects.all():
        cost[program.name] = 0
    for member in Member.objects.all():
        if not member.staff:
            for membership in member.memberships:
                # Divide the income between the programs.
                num_programs = len(membership.programs.all())
                for program in membership.programs:
                    cost[program.name] += membership.price / num_programs
    context['analysis'] = cost
    return render(request,'final_project/analysis.html',context)
