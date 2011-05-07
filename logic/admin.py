from google.appengine.api import mail
from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.db import Key
from google.appengine.api import urlfetch
from google.appengine.api import images
import png
import cgi
import logging
import os
import sys
import wsgiref.handlers
import uuid
import urlparse
import urllib2
import random
from BeautifulSoup import ICantBelieveItsBeautifulSoup as ICBS
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import *
from django.utils import simplejson as json
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')

class MainPage(webapp.RequestHandler):
    def get(self):
        return
    
