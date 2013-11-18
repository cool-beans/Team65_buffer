from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

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
        staff = program.staff
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
    try:
        staff_member = Staff.objects.get(member=member)
        member = Member.objects.get(id=member_id)

    # They are not staff. Only let them see their own profile.
    except Staff.DoesNotExist:
        member = Member.objects.get(user=request.user)
    except Member.DoesNotExist:
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

    try:
        staff_member = Staff.objects.get(member=member)
    except Staff.DoesNotExist:
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
    try:
        staff_member = Staff.objects.get(member=member)
    except Staff.DoesNotExist:
        # Make sure that the currently logged in user is a staff member
        if (staff_member is None):
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
        return rendder(request,'final_project/program_edit.html',context)
    if (form.cleaned_data['name']):
        program.name = form.cleaned_data['name']
    if (form.cleaned_data['description']):
        program.description = form.cleaned_data['description']
    program.save()
    context = {'user':request.user,
               'program':program}
    return render(request,'final_project/program_profile.html',context)

