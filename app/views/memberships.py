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


# Buy a membership.
@login_required
def buy(request,membership_type_id):
    user = request.user
    member = Member.objects.get(user=request.user)
    context = {'user':user,'member':member}


    if request.method == 'GET': # If we are trying to get the page.
        if len(MembershipType.objects.filter(id__exact=membership_type_id)) == 0:
            context['errors'] = ['Error, no such membership.']
            context['memberships'] = MembershipType.objects.all()
            return render(request,'final_project/Memberships/memberships.html',context)
        context['membership_type'] = MembershipType.objects.get(id__exact=membership_type_id)
        return render(request, 'final_project/Memberships/buy_membership.html',context)

    # Try to get the membership to edit. If there isn't one then render an error.
    try:
        mem_type = MembershipType.objects.get(id__exact=membership_type_id)
    except MembershipType.DoesNotExist:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/Memberships/buy_membership.html',context)

    # If there is no price specified just use the default price.
    if not 'default_price' in request.POST or not request.POST['default_price'] or not member.staff:
        price = mem_type.default_price
    else: price = int(request.POST['default_price'])
    # If there is no variable buy_user then we are buying for ourselves.
    if not 'buy_user' in request.POST or not request.POST['buy_user']:
        buy_member = member
    # If we are not buying for ourself then we have to be staff.
    elif not member.staff:
        context['errors'] = ['Error: Only Staff members can buy memberships for other members.']
        return render(request, 'final_project/Memberships/buy_membership.html',context)
    # Now we know we are staff and
    else:
        try:
            buy_user = User.objects.get(username=request.POST['buy_user'])
        except User.DoesNotExist:
            context['errors'] = ['Error, there is no such member.']
            return render(request, 'final_project/Memberships/buy_membership.html',context)
        buy_member = Member.objects.get(user=buy_user)


    # Create a new membership.

    membership = Membership(price=price,
                            mem_type=mem_type,
                            creation_date=datetime.now(),
                            member=buy_member)
    if 'exp_date' in request.POST and request.POST['exp_date']:
        membership.exp_date = request.POST['exp_date']
    membership.member = buy_member
    membership.save()

    context['membership'] = membership
    context['alerts'] = ['Successfully bought membership.']
    context['user'] = buy_member.user
    context['member'] = buy_member
    context['programs'] = buy_member.program_set.all()

    # If the membership has programs associated with it we need to divide the
    # revenue or payroll amongst the memberships.
    if len(membership.mem_type.program_set.all()) > 0:
        price_add = price / len(membership.mem_type.program_set.all())
        for program in membership.mem_type.program_set.all():
            if buy_member.staff:
                program.payroll += price_add
            else:
                program.revenue += price_add
            program.save()



    # Send the receipt for the membership.
    email_content = """
%s--
Thank you for your purchase of %s for $%s per month!

If you have any questions please let our staff know.

--Guitar Studio
""" % (buy_member.first_name, membership.name(),membership.price)
    send_mail(subject="Receipt",
              message=email_content,
              from_email="guitar@studio.com",
              recipient_list=[buy_member.email])


    context['memberships'] = Membership.objects.filter(member=buy_member)
    return render(request, 'final_project/Members/member_profile.html', context)


# Cancel a membership.
@login_required
def cancel(request,membership_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Try to get the membership.
    try:
        membership = Membership.objects.get(id__exact=membership_id)
    except Membership.DoesNotExist:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/Memberships/member_profile.html',context)
    # Either they are staff or they need to own that particular membership
    if member.membership_set.filter(id__exact=membership_id).count() == 0 and \
            not member.staff:
        context['errors'] = ['Error: You do not have access to that membership.']
        return render(request, 'final_project/Memberships/member_profile.html',context)

    # If the membership has programs associated with it we need to divide the
    # revenue or payroll amongst the memberships.
    if len(membership.mem_type.program_set.all()) > 0:
        price_add = membership.price / len(membership.mem_type.program_set.all())
        for program in membership.mem_type.program_set.all():
            if membership.member.staff:
                program.payroll -= price_add
            else:
                program.revenue -= price_add
            program.save()

    # Cancel the membership.
    membership.cancelled = True
    membership.cancelled_date = datetime.now()
    membership.save()
    context['member'] = membership.member
    return render(request,'final_project/Members/member_profile.html',context)

# Serve all memberships.
def all(request):
    context = {}
    if  request.user.is_authenticated():
        context['user'] = request.user
        context['member'] = Member.objects.get(user=request.user)
    context['memberships'] = MembershipType.objects.all()
    return render(request,'final_project/Memberships/memberships.html',context)


# Create a new type of membership.
@login_required
def create_type(request):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Only staff members can create membership types.
    if not member.staff:
        context['errors'] = ['Error: This page requires staff login.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    if request.method == 'GET': # If we are trying to get the page.
        return render(request, 'final_project/Memberships/membershiptype_create.html',context)
    # Get and sanitize the data.
    form = MembershipTypeCreate(request.POST)
    if not form.is_valid():
        context['errors'] = ['Error: Bad membership data']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    form.save()
    m_type = MembershipType.objects.get(name=form.cleaned_data['name'])
    context['membership_type'] = m_type
    return render(request,'final_project/Memberships/membershiptype_view.html',context)


# Edit a membership type.
@login_required
def edit_type(request,membership_type_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Only staff can edit memberships.
    if not member.staff:
        context['errors'] = ['Error: That page requires staff access.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    try:
        # Try to get the membership.
        mem_type = MembershipType.objects.get(id__exact=membership_type_id)
    except MembershipType.DoesNotExist:
        # If there is no such membership return an error.
        context['errors'] = ['Error: Could not find membership to edit.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)

    if request.method == 'GET': # If we are trying to get the page.
        context['membership_type'] = mem_type
        in_program = mem_type.program_set.all()
        not_in_program = list(set(Program.objects.all()) - set(in_program))
        context['in_program'] = in_program
        context['not_in_program'] = not_in_program
        return render(request,'final_project/Memberships/membershiptype_edit.html',context)

    # If the data is given then modify it.
    if 'name' in request.POST and request.POST['name']:
        mem_type.name = request.POST['name']
    if 'description' in request.POST and request.POST['description']:
        mem_type.description = request.POST['description']
    if 'default_price' in request.POST and request.POST['default_price']:
        mem_type.default_price = request.POST['default_price']
    if 'allowed_freq' in request.POST and request.POST['allowed_freq']:
        mem_type.allowed_freq = request.POST['allowed_freq']


    # Look through each program and see if the name is in the POST
    for prog in Program.objects.all():
        name = prog.name
        # If it is then add or remove depending on the content.
        if name in request.POST and request.POST[name]:
            if request.POST[name] == 'add':
                prog.memberships.add(mem_type)
            elif request.POST[name] == 'remove':
                prog.memberships.remove(mem_type)
            prog.save()

    mem_type.save()
    context['membership_type'] = mem_type
    context['alerts'] = ['Successfully changed Membership.']
    context['memberships'] = MembershipType.objects.all()
    return render(request,'final_project/Memberships/memberships.html', context)

