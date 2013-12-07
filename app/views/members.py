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
from app.views.common import helper_paginator


def register(request):
    context = {}
    errors = []

    # If simply requesting the register page
    if request.method == 'GET':
        context['errors'] = errors
        return render(request, 'final_project/Members/register.html', context)

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
    return render(request, 'final_project/Members/register.html', context)

# Serve all of the programs and members.
@login_required
def all(request):
    context = {}
    members = Member.objects.order_by('first_name').all()
    context['user'] = request.user
    context['members'] = helper_paginator(members,10,request.GET.get('page'))
    context['should_paginate'] = 10 < len(members)
    context['programs'] = Program.objects.all()
    return render(request, 'final_project/Members/members.html', context)

# Serve only the members who are in the program with id program_id.
# If there is no such program, serve all members.
@login_required
def filter (request, program_id):
    context = {}
    user = request.user
    members = []
    try:
        program = Program.objects.get(id=program_id)
        members = Member.objects.filter(program=program).order_by('first_name')
    except Program.DoesNotExist:
        members = Member.objects.all()


    context['user'] = user
    context['members'] = helper_paginator(members,10,request.GET.get('page'))
    context['should_paginate'] = 10 < len(members)
    context['programs'] = Program.objects.all()
    return render(request, 'final_project/Members/members.html', context)


# Serve the members profile. If the member is staff then they can see whoever
# they want to, otherwise redirect to their own profile.
@login_required
def profile(request, member_id):
    context = {}
    user = request.user
    member = Member.objects.get(user=user)

    # Are they staff? If so then let them see whoever
    if member.staff:
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            member = Member.objects.get(user=user)
    # They are not staff. Only let them see their own profile.
    else:
        member = Member.objects.get(user=request.user)


    context['user'] = user
    context['member'] = member
    context['programs'] = member.program_set.all()
    context['memberships'] = Membership.objects.filter(member=member)
    return render(request, 'final_project/Members/member_profile.html', context)

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
def edit(request, member_id):
    context = {}
    user = request.user
    member = Member.objects.get(user=user)
    errors = []

    # Try to get the member to edit. If there is no such member then render an error.
    try:
        old_member = Member.objects.get(id=member_id)
    except Member.DoesNotExist:
        context['errors'] = ['Error: Could not find member to edit']
        context['members'] = Member.objects.order_by('first_name').all()
        return render(request,'final_project/members.html',context)

    # If simply getting the page to edit
    if request.method == 'GET':
        in_program = old_member.program_set.all()
        not_in_program = list(set(Program.objects.all()) - set(in_program))

        context['in_program'] = in_program
        context['not_in_program'] = not_in_program


    # If trying to save changes to member
    elif request.method == 'POST':
        form = MemberEdit(request.POST)
        # Sanitize the data.
        if not form.is_valid():
            errors.append('Error, bad form data')
            context = {'user':user,'member':member,
                       'errors':errors}
            return render(request,'final_project/Members/member_edit.html',context)
        else:
            old_user = old_member.user
            # If each field is present then change the data.
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

            # If we are trying give/remove user staff access then verify
            # that the user who is currently editing is staff.
            if 'make_staff' in request.POST and member.staff:
                old_member.staff = True
            if 'remove_staff' in request.POST and member.staff:
                old_member.staff = False
            old_member.save()
            context['user'] = user
            context['member'] = old_member
            context['errors'] = errors
            # Look through each program and see if the name is in the POST
            for prog in Program.objects.all():
                name = prog.name
                # If it is then add or remove depending on the content.
                if name in request.POST and request.POST[name]:
                    if request.POST[name] == 'remove':
                        prog.members.remove(old_member)
                    elif request.POST[name] == 'add':
                        prog.members.add(old_member)
                    prog.save()

            return redirect('/final_project/member_profile/' + member_id)

    context['user'] = user
    context['member'] = member
    context['member_to_edit'] = old_member
    context['errors'] = errors
    return render(request, 'final_project/Members/member_edit.html', context)


# Search for a user from a string.
@login_required
def search(profile):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Only staff can search.
    if not member.staff:
        context['errors'] = ['Error: Only staff members can search for members.']
        context['programs'] = member.program_set.all()
        context['memberships'] = Membership.objects.filter(member=member)
        return render(request,'final_project/Members/member_profile',context)

    # Verify that a string was given.
    if not 'search' in request.POST or not request.POST['search']:
        context['errors'] = ['Error: Bad search string.']
        context['members'] = Member.objects.order_by('first_name').all()
        context['programs'] = Program.objects.all()
        return render(request,'final_project/Members/members.html',context)

    # Search in first and last name.
    search = request.POST['search']
    context['members'] = Member.objects.filter(Q(first_name__contains=search) | \
                                                   Q(last_name__contains=search))

    return render(request,'final_project/Members/members.html',context)


