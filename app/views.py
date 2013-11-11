from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

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

			# Create a new member and associate it with the new user
			new_member = Member(user=new_user,\
								first_name=request.POST['first_name'],\
								last_name=request.POST['last_name'],\
								birthday=request.POST['birthday'],\
								phone=request.POST['phone'],\
								email=request.POST['email'],\
								enroll_date=datetime.now())
			new_member.save()

			# Logs in new user and redirects to their member_profile page
			new_user = authenticate(username=request.POST['username'], \
									password=request.POST['pass1'])
			login(request, new_user)

			return redirect('/final_project/member_profile/' + new_user_id)

    context['errors'] = errors
    return render(request, 'final_project/register.html', context)

@login_required
def members(request):
    context = {}
    user = request.user
    members = []

    # If simply requesting members page, no filtering
    if request.method == 'GET':
    	members = Member.objects.all().order_by('first_name')

    # Should never be 'POST'
    elif request.method == 'POST':
    	pass

    context['user'] = user
    context['members'] = members
    return render(request, 'final_project/members.html', context)

@login_required
def filter_members (request, program_id):
	context = {}
	user = request.user
	program = Program.objects.get(id=program_id)
	members = Member.objects.filter(program=program).order_by('first_name')

	context['user'] = user
	context['members'] = members
	return render(request, 'final_project/members.html', context)

@login_required
def member_profile(request, member_id):
    context = {}
    user = request.user
    member = None

    # If request was a GET, means it got redirected here from the register
    # page. Or the user wanted to view their own profile.
    # Which means should just display the current user's own profile
    if request.method == 'GET':
    	member = user.member

    # If the request was a POST, means it is a staff member trying to
    # view a specific member's profile
    elif request.method == 'POST':
    	member = Member.objects.get(id=member_id)

    context['user'] = user
    context['member'] = member
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
	member = None

	# If simply getting the page to edit
	if request.method == 'GET':
		member = Member.objects.get(id=member_id)

	# If trying to save changes to member
	elif request.method == 'POST':
		# Gigantic if statement checking if form is valid and fields are
    	# not blank
    	if not 'pass1' in request.POST or not request.POST['pass1']\
    		or not 'pass2' in request.POST or not request.POST['pass2']\
    		or not 'first_name' in request.POST or not request.POST['first_name']\
    		or not 'last_name' in request.POST or not request.POST['last_name']\
    		or not 'birthday' in request.POST or not request.POST['birthday']\
    		or not 'phone' in request.POST or not request.POST['phone']\
    		or not 'email' in request.POST or not request.POST['email']:

    		errors.append('Missing a field.')
    		
    	# Check to make sure passwords match
    	elif request.POST['pass1'] != request.POST['pass2']:
    		errors.append('Passwords do not match.')
    	
    	# Check to make sure phone is 10 digits
    	elif len(request.POST['phone']) != 10:
    		errors.append('Phone must be 10 digits.')

    	# Data was all clean, can modify and save old_user and old_member
    	# Then redirect to member_profile.html
    	else:
    		old_member = Member.objects.get(id=member_id)
    		old_user = old_member.user

    		# Change the password of the old_user and save the old_user.
    		old_user.password = request.POST['pass1']
    		old_user.save()

    		# Change first_name, last_name, birthday, phone, and email 
    		# of the old_member and save the old_member
    		old_member.first_name = request.POST['first_name']
    		old_member.last_name = request.POST['last_name']
    		old_member.birthday = request.POST['birthday']
    		old_member.phone = request.POST['phone']
    		old_member.email = request.POST['email']
    		old_member.save()
    		return redirect('/final_project/member_profile/' + member_id)

	context['user'] = user
	context['member'] = member
	return render(request, 'final_project/member_edit.html', context)