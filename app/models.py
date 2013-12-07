from django.db import models
from django.db.models import Q

from datetime import *
import re

# User class for built-in authentication module
from django.contrib.auth.models import User

class Member(models.Model):
    # Members can be Staff
    # Many Members can attend many Events
    # Many Members can be part of many Programs
    # Members have many Attendence for events
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birthday = models.DateField()

    phone = models.CharField(max_length=10)
    email = models.CharField(max_length=30)

    staff = models.BooleanField(default=False)

    creation_date = models.DateField()

    def active_memberships(self):
        return self.membership_set.filter(cancelled=False)
    def cancelled_memberships(self):
        return self.membership_set.filter(cancelled=True)
    #programs = models.ManyToManyField(Program)
    #events = models.ManyToManyField(Event)
    def name(self):
        return self.first_name+" "+self.last_name
    def __unicode__(self):
        return self.first_name + " " + self.last_name
    @staticmethod
    def getcount():
        return Member.objects.count()

class MembershipType(models.Model):
    # Membership Types for members
    # These contain the name, description, and programs.
    # These are what we display to the users.

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    allowed_freq = models.IntegerField()
    default_price = models.IntegerField()
    visible = models.BooleanField()
    def __unicode__(self):
        return self.name

class Membership(models.Model):
    # This is the membership that we sell to the individual member.
    price = models.DecimalField(max_digits=7, decimal_places=2)
    mem_type = models.ForeignKey(MembershipType)
    exp_date = models.DateField(null=True, blank=True)
    creation_date = models.DateField()
    cancelled = models.BooleanField()
    cancelled_date = models.DateField(null=True,blank=True)
    member = models.ForeignKey(Member)
    def name(self):
        return self.mem_type.name
    def description(self):
        return self.mem_type.description
    def __unicode__(self):
        return self.mem_type.name

    @staticmethod
    def total_revenue():
        rev = 0
        for member in Member.objects.filter(staff=False):
            for m in member.membership_set.filter(cancelled=False):
                rev += m.price
        return rev

    @staticmethod
    def total_payroll():
        pay = 0
        for member in Member.objects.filter(staff=True):
            for m in member.membership_set.filter(cancelled=False):
                pay += m.price
        return pay


    @staticmethod
    def total_profit():
        return Membership.total_revenue() - Membership.total_payroll()



class Program(models.Model):
    # Many EventTypes in many Programs
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    members = models.ManyToManyField(Member)
    revenue = models.IntegerField(default=0)
    payroll = models.IntegerField(default=0)
    memberships = models.ManyToManyField(MembershipType)
    def profit(self):
        return self.revenue - self.payroll
    def __unicode__(self):
        return self.name
    

class RecurringEvent(models.Model):
    LOWER = datetime(2013,1,1)
    UPPER = datetime(2015,12,31)
    onMonday = models.BooleanField(default=False)
    onTuesday = models.BooleanField(default=False)
    onWednesday = models.BooleanField(default=False)
    onThursday = models.BooleanField(default=False)
    onFriday = models.BooleanField(default=False)
    onSaturday = models.BooleanField(default=False)
    onSunday = models.BooleanField(default=False)
    # Has many Events associated with one EventType
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True,null=True)
    programs = models.ManyToManyField(Program)
    default_start_time = models.TimeField()
    default_end_time = models.TimeField()

    def spawn_events(self):
        d = self.start_date
        days = []
        # Get the days you recur.
        if self.onMonday: days.append(0)
        if self.onTuesday: days.append(1)
        if self.onWednesday: days.append(2)
        if self.onThursday: days.append(3)
        if self.onFriday: days.append(4)
        if self.onSaturday: days.append(5)
        if self.onSunday: days.append(6)

        # If there is an end date defined stop then otherwise stop at the
        # upper bound for events.
        if self.end_date: stop = self.end_date
        else: stop = UPPER

        while d < stop:
            weekday = d.weekday()
            # If the day is in the recurrence generate an event.
            if weekday in days:
                e = Event(date=d,start_time=self.default_start_time,
                          end_time=self.default_end_time,recurrence=self)
                e.save()
            d = d + timedelta(1)

# This is the physical calender event generated by an EventType
# which may repeatedly generate events (i.e. for every Tuesday)
# Otherwise, how would you delete a recurring event
# for just one day?
class Event(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    recurrence = models.ForeignKey(RecurringEvent,blank=True,null=True)
    booked = models.ManyToManyField(Member,related_name="booked")
    attended = models.ManyToManyField(Member,related_name="attended")
    cancelled = models.ManyToManyField(Member,related_name="cancelled")
    # These are only needed if it is not a recurring event.
    name = models.CharField(max_length=100,blank=True,null=True)
    description = models.CharField(max_length=500, blank=True,null=True)
    price = models.IntegerField(blank=True,null=True)

    def get_name(self):
        if self.name: return self.name
        else: return self.recurrence.name
    def get_description(self):
        if self.description: return self.description
        else: return self.recurrence.description

