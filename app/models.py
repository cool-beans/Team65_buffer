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



class Program(models.Model):
    # Many EventTypes in many Programs
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=500)
    members = models.ManyToManyField(Member)
    revenue = models.IntegerField(default=0)
    payroll = models.IntegerField(default=0)
    memberships = models.ManyToManyField(MembershipType)
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

    # Given num, return string equivalent for the day
    # {0:'Monday', 1: 'Tuesday', 2: 'Wednesday', etc.}
    @staticmethod
    def dayNum2Str(num):
        num2str = { 0: 'Monday',
                    1: 'Tuesday',
                    2: 'Wednesday',
                    3: 'Thursday',
                    4: 'Friday',
                    5: 'Saturday',
                    6: 'Sunday' }
        return num2str[num]


    # Given a date, Recurrence checks if the date is valid
    # for the Recurrence. If valid, return True. Else: False
    def isValidDate(self, date):
        weekdays = self.getDays()

        # Check date's weekday is one of the recurring weekdays
        # and if start_date is before/on date
        # and either no end_recurrence or end_recurrence is on/after date
        if ( (date.weekday() in weekdays) and \
             (self.start_date <= date) and \
             ( (not self.end_recurrence) or (self.end_recurrence >= date) ) ):
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

    def eventOnDate(self, date):
        date = None

        return date

    # Just prints out all the information for all EventType
    @staticmethod
    def printAllTypes():
        print "\n\n***************EVENT TYPES START***************"
        for event in EventType.objects.all():
            print "name: " + event.name
            print "start_date: " + str(event.recurrence.start_date)
            print "end_recurrence: " + str(event.recurrence.end_recurrence)
            print "start_time: " + str(event.start_time)
            print "days: " + str(event.recurrence.getDays())
            print "--------------------------------------"
        print "***************EVENT TYPES END***************\n\n"


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
                    if (weekday in eventtype.recurrence.getDays() or weekday == eventtype.recurrence.start_date.weekday()):
                        # (if we got this far, means no Event already exists)
                        # Create an event!
                        event = eventtype.createEvent(date)
                        print "EVENT CREATED!"
                        break
        return event

    # Given date, returns a list of all the events that occur on that day.
    @staticmethod
    def getEventsOnDate(date):
        events = []

        # Get existing events first
        events += Event.objects.filter(date=date)

        # Get recurrences that have a start_date before/on date
        recurrences = Recurrence.objects.filter(start_date__lte=date)
        # Filter for recurrences that have no end_recurrence or one on/after date
        recurrences = recurrences.filter(Q(end_recurrence=None)|Q(end_recurrence__gte=date))

        for recurrence in recurrences:
            if recurrence.isValidDate(date):
                eventtype = recurrence.eventtype

                # Try to get event with the proper date and eventtype's name/start_time
                event = Event.getEvent(name=eventtype.name,
                                       date=date,
                                       start_time=eventtype.start_time)
                if event and event not in events:
                    events.append(event)

        # Lambda function to sort the list of events in place by start_time (most recent first)
        events.sort(key=lambda event: event.start_time) #, reverse=True)
        return events

    # Given sunday_date, return list of all events in that week
    @staticmethod
    def getEventsFromSunday(sunday_date):
        events = []
        day_to_events = {} # {'Monday': [event1, event2], ...}

        # Build list of dates in current week
        # Initialize day_to_events
        for i in range(0, 7):
            date_to_get = sunday_date - timedelta(days=i)

            weekday_num = date_to_get.weekday()
            weekday_str = Recurrence.dayNum2Str(weekday_num)

            # Get all events on the date and store them in dictionary
            day_to_events[weekday_str] = Event.getEventsOnDate(date_to_get)

        events += ( day_to_events['Monday'] + \
                    day_to_events['Tuesday'] + \
                    day_to_events['Wednesday'] + \
                    day_to_events['Thursday'] + \
                    day_to_events['Friday'] + \
                    day_to_events['Saturday'] + \
                    day_to_events['Sunday'] )

        return events
        # TODO: eventually want to return day_to_events!
        #return day_to_events

    # Given a string '1 a.m.' or '10:22 p.m.' etc, return the
    # datetime object. Returns '' if invalid t_in
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

    # Given list of events, prints their info out
    @staticmethod
    def printEvents(events):
        print "\n***************EVENTS IN WEEK START****************"
        for e in events:
            print "EVENT: " + e.name
            print "\tdate: " + str(e.date)
            print "\tdesc: " + e.description
        print "***************EVENTS IN WEEK END****************\n"

class Attendance(models.Model):
    member = models.ForeignKey(Member)
    event = models.ForeignKey(Event)
    sign_in_time = models.TimeField()

    def __unicode__(self):
        return self.sign_in_time
