from django.db import models
from django.db.models import Q

from datetime import *
import re

# User class for built-in authentication module
from django.contrib.auth.models import User

class MembershipType(models.Model):
    # Membership Types for members
    # These contain the name, description, and programs.
    # These are what we display to the users.

    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
#    programs = models.ManyToManyField(Program)
    allowed_freq = models.IntegerField()
    default_price = models.IntegerField()
    visible = models.BooleanField()
    def __unicode__(self):
        return self.name

class Membership(models.Model):
    # This is the membership that we sell to the individual member.
    price = models.DecimalField(max_digits=7, decimal_places=2)
    mem_type = models.OneToOneField(MembershipType)
    exp_date = models.DateField(null=True, blank=True)
    creation_date = models.DateField()
    cancelled = models.BooleanField()
    cancelled_date = models.DateField(null=True,blank=True)
    def __unicode__(self):
        return self.mem_type.name


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
    memberships = models.ManyToManyField(Membership)


    #programs = models.ManyToManyField(Program)
    #events = models.ManyToManyField(Event)

    def __unicode__(self):
        return self.first_name + " " + self.last_name

class Program(models.Model):
    # Many EventTypes in many Programs
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    members = models.ManyToManyField(Member)

    def __unicode__(self):
        return self.name

class Recurrence(models.Model):
    # Associated with one EventType
    onSundays = models.BooleanField(default=False)
    onMondays = models.BooleanField(default=False)
    onTuesdays = models.BooleanField(default=False)
    onWednesdays = models.BooleanField(default=False)
    onThursdays = models.BooleanField(default=False)
    onFridays = models.BooleanField(default=False)
    onSaturdays = models.BooleanField(default=False)

    isRecurring = models.BooleanField(default=False)

    start_date = models.DateField()
    end_recurrence = models.DateField(null=True, blank=True)

    def __unicode__(self):
        return self.eventtype.name + "'s Recurrence"

    def setDayRecurrence(self, day, isRecurring):
        if day == 'Monday':
            self.onMondays = isRecurring
        elif day == 'Tuesday':
            self.onTuesdays = isRecurring
        elif day == 'Wednesday':
            self.onWednesdays = isRecurring
        elif day == 'Thursday':
            self.onThursdays = isRecurring
        elif day == 'Friday':
            self.onFridays = isRecurring
        elif day == 'Saturday':
            self.onSaturdays = isRecurring
        elif day == 'Sunday':
            self.onSundays = isRecurring

    def getDays(self):
        days = []

        if self.onMondays:
            days.append(0)
        if self.onTuesdays:
            days.append(1)
        if self.onWednesdays:
            days.append(2)
        if self.onThursdays:
            days.append(3)
        if self.onFridays:
            days.append(4)
        if self.onSaturdays:
            days.append(5)
        if self.onSundays:
            days.append(6)

        return days

    # Given a date, Recurrence checks if the date is valid
    # for the Recurrence. If valid, return True. Else: False
    def isValidDate(self, date):
        weekdays = self.getDays()

        # Check date's weekday is one of the recurring weekdays
        # and if start_date is before/on date
        # and either no end_recurrence or end_recurrence is on/after date
        if ( (date.weekday() in weekdays) and \
             (self.start_date <= date) and \
             ( (not end_recurrence) or (end_recurrence >= date) ) ):
            # Is valid date!
            return True
        return False


class EventType(models.Model):
    # Has many Events associated with one EventType
    name = models.CharField(max_length=100)
    programs = models.ManyToManyField(Program)
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=500, blank=True)
    recurrence = models.OneToOneField(Recurrence)
    #allowed_memberships = models.ManyToManyField(Membership)

    def __unicode__(self):
        return self.name

    # Given date, creates a new Event for the EventType
    # and returns it without saving!
    def createEvent(self, date):
        event = Event(name=self.name,
                      date=date,
                      start_time=self.start_time,
                      end_time=self.end_time,
                      description=self.description,
                      event_type = self,
                      # Set original info
                      orig_name=self.name,
                      orig_date=date,
                      orig_start_time=self.start_time)
        return event

    def getEventsGivenSunday(self, sunday_date):
        events = []

        return events

    def eventOnDate(self, date):
        date = None

        return date

# This is the physical calender event generated by an EventType
# which may repeatedly generate events (i.e. for every Tuesday)
# Otherwise, how would you delete a recurring event
# for just one day?
class Event(models.Model):
    # Events are associated with an EventType

    # Set original event info only upon creation of Event!!
    orig_name = models.CharField(max_length=100)
    orig_date = models.DateField()
    orig_start_time = models.TimeField()

    name = models.CharField(max_length=100)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.CharField(max_length=500, blank=True)
    attendees = models.ManyToManyField(Member, null=True, blank=True)
    event_type = models.ForeignKey(EventType)
    is_cancelled = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    # Given actual name, date, start_time of an event (not original info)
    # find the specified event if it exists (or create a temp one)
    # and return it.
    # First check Events.objects, if no such event exists,
    # Second, find proper EventType and create a temp Event
    # Third, if no EventType matches, then return None
    @staticmethod
    def getEvent(name, date, start_time):

        event = None

        # First, check Events.objects for an event that fits given info
        events = Event.objects.filter(name=name).filter(date=date).filter(start_time=start_time)
        if events and len(events)==1:
            event = events[0]

        # If no events exist, first check for an event with matching
        # original data, if so, return null (don't check EventTypes!)
        events = Event.objects.filter(Q(orig_name=name), \
                                      Q(orig_date=date), \
                                      Q(orig_start_time=start_time))
        if events:
            return null

        # If you got here, no Event currently exists that is related to given info
        # Look for the proper EventType and create a temp Event to return without saving
        else:
            print 'getEvent: looking through EventTypes'
            print 'name: ' + name
            print 'date: ' + str(date)
            print 'time: ' + str(start_time)

            eventtypes = EventType.objects.filter(name=name).filter(start_time=start_time)

            for eventtype in eventtypes:
                print "EVENTTYPE----------------------------"
                print "name: " + eventtype.name
                print "date: " + str(eventtype.recurrence.start_date)
                print "time: " + str(eventtype.start_time)
                print "--------------------------------------\n"
                # If the event started before or on date and
                # either has no end_recurrence or an end_recurrence >= date,

                # If the event started before or on date and
                # either has no end_recurrence or an end_recurrence >= date,

                # then event may exist in this EventType! Check!
                if (eventtype.recurrence.start_date <= date and \
                    (not eventtype.recurrence.end_recurrence or \
                    eventtype.recurrence.end_recurrence >= date)):
                    print "WEEKDAY: " + str(date.weekday())
                    weekday = date.weekday()
                    print "eventtype weekday: " + str(eventtype.recurrence.start_date.weekday())
                    # If event's weekday was in eventtype's weekdays
                    if weekday in eventtype.recurrence.getDays() or weekday == eventtype.recurrence.start_date.weekday():
                        # (if we got this far, means no Event already exists)
                        # Create an event!
                        event = eventtype.createEvent(date)
                        print "EVENT CREATED!"
                        break
        return event

    @staticmethod
    def convertTime(t_in):
        t_out = ''
        t_temp = t_in.replace('.', "")
        pattern = r"(?P<hr>\d+)(:)?(?(2)(?P<min>\d{2})) (?P<ampm>am|pm)"
        parsed = ''

        match = re.search(pattern, t_temp)
        # Check for a match
        if match:
            d = match.groupdict()
            # Check for hour, min, am|pm and format them
            if ('hr' in d.keys() and 'min' in d.keys() and \
                'ampm' in d.keys()):
                hr = d['hr']
                min = d['min']
                ampm = d['ampm']
                # Format hour 'HH'
                if len(hr) == 1:
                    hr = '0' + hr
                # Format minute 'MM'
                if not min:
                    min = '00'
                parsed = hr + ':' + min + ' ' + ampm

        if parsed:
            # parsed now in format HH:MM (AM|PM), get time object
            t_out = datetime.strptime(parsed, '%I:%M %p').time()

        return t_out

    # Given a date, return the date of the Sunday of that week!
    @staticmethod
    def getSundayDate(date):
        SUNDAY = 6
        sunday_date = None
        # Loop through possible dates from given date through date + 6
        for i in range(0, 7):
            checking_date = date + timedelta(days=i)
            if checking_date.weekday() == SUNDAY:
                sunday_date = checking_date
                break
        return sunday_date

    #@staticmethod
    #def convertDate():
    # TODO: toy with idea of making convertTime/convertDate simply return datetime.time/datetime.date objects

class Attendance(models.Model):
    member = models.ForeignKey(Member)
    event = models.ForeignKey(Event)
    sign_in_time = models.TimeField()

    def __unicode__(self):
        return self.sign_in_time
