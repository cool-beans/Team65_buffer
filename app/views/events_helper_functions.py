from app.models import *

# Helper Functions for events

def getContextForAll(user, errors, sunday_date):
    context = {}

    events = []
    monday_events = []
    tuesday_events = []
    wednesday_events = []
    thursday_events = []
    friday_events = []
    saturday_events = []
    sunday_events = []

    events = Event.getEventsFromSunday(sunday_date)

    context['user'] = user
    context['sunday_date'] = sunday_date
    context['events'] = events
    context['errors'] = errors
    return context
