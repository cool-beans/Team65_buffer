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



@login_required
def buy(request,membership_type_id):
    user = request.user
    member = Member.objects.get(user=request.user)
    context = {'user':user,'member':member}

    # Sanitize the data.
    if request.method == 'GET':
        if len(MembershipType.objects.filter(id__exact=membership_type_id)) == 0:
            context['errors'] = ['Error, no such membership.']
            context['memberships'] = MembershipType.objects.all()
            return render(request,'final_project/Memberships/memberships.html',context)
        context['membership_type'] = MembershipType.objects.get(id__exact=membership_type_id)
        return render(request, 'final_project/Memberships/buy_membership.html',context)
    try:
        mem_type = MembershipType.objects.get(id__exact=membership_type_id)
    except MembershipType.DoesNotExist:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/Memberships/buy_membership.html',context)

    # If there is no price specified just use the default price.
    if not 'price' in request.POST or not request.POST['price'] or not member.staff:
        price = mem_type.default_price
    else: price = request.POST['price']

    if not 'buy_user' in request.POST or not request.POST['buy_user']:
        buy_member = member
    elif not member.staff:
        context['errors'] = ['Error: Only Staff members can buy memberships for other members.']
    else:
        buy_user = User.objects.get(username=request.POST['buy_user'])
        buy_member = Member.objects.get(user=buy_user)

    if len(buy_member.memberships.filter(mem_type=mem_type)) > 0:
        context['errors'] = ['Error: Cannot buy two copies of the same membership.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)

    # Create a new membership.
    membership = Membership(price=price,mem_type=mem_type)
    if 'exp_date' in request.POST and request.POST['exp_date']:
        membership.exp_date = request.POST['exp_date']
    membership.creation_date = datetime.now()
    membership.save()
    buy_member.memberships.add(membership)
    buy_member.save()
    context['membership'] = membership
    return render(request,'final_project/Memberships/memberships.html', context)


@login_required
def cancel(request,membership_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Try to get the membership.
    try:
        mem = Membership.objects.get(id__exact=membership_id)
    except Membership.DoesNotExist:
        context['errors'] = ['Error: Could not find membership.']
        return render(request,'final_project/Memberships/member_profile.html',context)
    # Either they are staff or they need to own that particular membership
    if member.memberships.filter(id__exact=membership_id).count() == 0 and \
            not member.staff:
        context['errors'] = ['Error: You do not have access to that membership.']
        return render(request, 'final_project/Memberships/member_profile.html',context)

    # Cancel the membership.
    mem.cancelled = True
    mem.cancelled_date = datetime.now()
    mem.save()
    return render(request,'final_project/Memberships/member_profile.html',context)

def all(request):
    context = {}
    if request.user is not None:
        context['user'] = request.user
        context['member'] = Member.objects.get(user=request.user)
    context['memberships'] = MembershipType.objects.all()
    return render(request,'final_project/Memberships/memberships.html',context)

@login_required
def create_type(request):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    if not member.staff:
        context['errors'] = ['Error: This page requires staff login.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    if request.method == 'GET':
        return render(request, 'final_project/Memberships/membershiptype_create.html',context)
    form = MembershipTypeCreate(request.POST)
    if not form.is_valid():
        context['errors'] = ['Error: Bad membership data']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    form.save()
    m_type = MembershipType.objects.get(name=form.cleaned_data['name'])
    context['membership_type'] = m_type
    return render(request,'final_project/Memberships/membershiptype_view.html',context)

@login_required
def view_type(request,membership_type_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    # Does the membership exist?
    try:
        mem_type = MembershipType.get(id__exact=membership_type_id)
        context['membership_type'] = mem_type
    except MembershipType.DoesNotExist:
        context['errors'] = ['Error: No such membership']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    if not mem_type.visible and not member.staff:
        context['errors'] = ['Error: No such membership']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    return render(request,'final_project/Memberships/view_membershiptype.html',context)

@login_required
def edit_type(request,membership_id):
    user = request.user
    member = Member.objects.get(user=user)
    context = {'user':user,'member':member}
    if not member.staff:
        context['errors'] = ['Error: That page requires staff access.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)


    # Try to get the membership.
    try:
        mem_type = MembershipType.objects.get(id__exact=membership_id)
    except MembershipType.DoesNotExist:
        context['errors'] = ['Error: Could not find membership to edit.']
        context['memberships'] = MembershipType.objects.all()
        return render(request,'final_project/Memberships/memberships.html',context)
    if 'name' in request.POST and request.POST['name']:
        mem_type.name = request.POST['name']
    if 'description' in request.POST and request.POST['description']:
        mem_type.description = request.POST['description']
    if 'default_price' in request.POST and request.POST['default_price']:
        mem_type.default_price = request.POST['default_price']
    mem_type.save()
    context['membership_type'] = mem_type
    return render(request,'final_project/Memberships/view_membershiptype.html', context)
