from django import template
from django.core.urlresolvers import reverse

register = template.Library()
@register.simple_tag
def get_nav_page_class(request,urls):
   if request.path in ( reverse(url) for url in urls.split() ):
      return "active"
   return ""
@register.simple_tag
def format_date_or_time(date):
   return str(date)
