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
import struct
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
import itertools
import operator
import hashlib
import math
import gviz_api

class Promising(db.Model):
    values = db.ListProperty(float)
    str_values = db.StringProperty()
    point_blob = db.BlobProperty()
       # stores every 10th value -- 'x,y,x,y,...'
       # watch out for the trailing comma
    good = db.BooleanProperty()
    checked = db.BooleanProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        my_range = self.request.get('my_range')

        if not my_range:
            self.response.out.write('<html><body><a href="/graphs/page">Rate Orbits as Good or Bad</a><br /><a href="/all/orbits">All Starting Positions, With Links to Graphs</a>')
            return

        my_range = int(my_range)
        
        def par(my_range, i):
            return 1.0*i/(my_range-1)

        for i in range(my_range):
            for j in range(my_range):
                for k in range(my_range):
                    for l in range(my_range):
                        x = par(my_range, i)
                        y = par(my_range, j)
                        vx = par(my_range, k)
                        vy = par(my_range, l)
                        taskqueue.add(queue_name='optimize',
                                      url='/test/starting/position',
                                      params={'x':x, 'y':y, 'vx':vx, 'vy':vy},
                                      method='GET')
      

        directory = os.path.dirname(__file__)
        path = os.path.join(directory, '../templates/front_page.html')
        #self.response.out.write(template.render(path, template_values))
        self.response.out.write('added them all!')

class TestStartingPosition(webapp.RequestHandler):
    def get(self):
        def step((x,y,vx,vy,t,dt,tracker)):
            vxtemp = vx
            vytemp = vy

            x = x + vx*0.5*dt
            y = y + vy*0.5*dt

            t = t + 0.5*dt

            r1x = 0.5*math.cos(t)
            r1y = 0.5*math.sin(t)
            r2x = -0.5*math.cos(t)
            r2y = -0.5*math.sin(t)
            d13 = pow(math.sqrt(pow(x-r1x,2)+pow(y-r1y,2)),3)
            d23 = pow(math.sqrt(pow(x-r2x,2)+pow(y-r2y,2)),3)
            ax = -0.5*((x-r1x)/d13 + (x-r2x)/d23)
            ay = -0.5*((y-r1y)/d13 + (y-r2y)/d23)

            vx = vx + ax*dt
            vy = vy + ay*dt

            x = x + vx*0.5*dt
            y = y + vy*0.5*dt

            t = t + 0.5*dt

            if math.fabs(vxtemp - vx) < 0.0001 and math.fabs(vytemp - vy) < 0.001:
                tracker += 1

            if (ay != 0 and y != 0) and math.fabs(ax/ay - x/y) < 0.001:
                tracker += 1
            else:
                tracker = 0

            return (x,y,vx,vy,t,dt,tracker)



        def test(ran, next):
            for i in range(ran):
                next = step(next)
                if next[-1] > 10:
                    return (100,100)
            return next

        x = float(self.request.get('x'))
        y = float(self.request.get('y'))
        vx = float(self.request.get('vx'))
        vy = float(self.request.get('vy'))

        tryit = test(100000, step((x,y,vx,vy,0,0.001,0)))

        if math.fabs(tryit[0]) < 50 and math.fabs(tryit[1]) < 50:
            new_promise = Promising()
            new_promise.values = [x,y,vx,vy]
            new_promise.put()
            logging.info('put  [%s,%s,%s,%s]', str(x), str(y), str(vx), str(vy))

        else:
            logging.info('didn\'t put [%s,%s,%s,%s]', str(x), str(y), str(vx), str(vy))
        
class ConvertToString(webapp.RequestHandler):
    query = db.Query(Promising)
    results = query.fetch(1000)
    for result in results:
        L = result.values
        result.str_values = str(L[0]) + ',' + str(L[1]) + ',' + str(L[2]) + ',' + str(L[3])
        result.put()
        
    
class SendCalcToQueues(webapp.RequestHandler):
    def get(self):
        query = db.Query(Promising)
        results = query.fetch(1000)
        for result in results:
            if not result.point_blob:
                taskqueue.add(queue_name='optimize',
                              url='/calc/points',
                              params={'str_values':result.str_values,},
                              method='GET')
    
class CalcPoints(webapp.RequestHandler):
    def get(self):
        try:
            # we'll only store every 5th value
            str_values = self.request.get('str_values')
            query = db.Query(Promising)
            query_filter = query.filter('str_values =', str_values)
            result = query_filter.get()
            L = result.values

            if result.point_blob:
                logging.info('already has point blob')
                return

            logging.info('no point blob')

            result.point_blob = ''

            next = self.step((L[0], L[1], L[2], L[3], 0, 0.001, 0))

            for i in range(100000):
                next = self.step(next)
                if i%10 == 0:
                    result.point_blob += "%.4f" % next[0] + ',' "%.4f" % next[1] + ','

            result.put()

            logging.info('put all the point values')

        except:
            logging.exception('exception')
            self.error(505)
        
    def step(self,(x,y,vx,vy,t,dt,tracker)):
        vxtemp = vx
        vytemp = vy

        x = x + vx*0.5*dt
        y = y + vy*0.5*dt

        t = t + 0.5*dt

        r1x = 0.5*math.cos(t)
        r1y = 0.5*math.sin(t)
        r2x = -0.5*math.cos(t)
        r2y = -0.5*math.sin(t)
        d13 = pow(math.sqrt(pow(x-r1x,2)+pow(y-r1y,2)),3)
        d23 = pow(math.sqrt(pow(x-r2x,2)+pow(y-r2y,2)),3)
        ax = -0.5*((x-r1x)/d13 + (x-r2x)/d23)
        ay = -0.5*((y-r1y)/d13 + (y-r2y)/d23)

        vx = vx + ax*dt
        vy = vy + ay*dt

        x = x + vx*0.5*dt
        y = y + vy*0.5*dt

        t = t + 0.5*dt

        return (x,y,vx,vy,t,dt,tracker)

class ReturnGraphData(webapp.RequestHandler):
    def get(self):
        str_values = self.request.get('str_value')
        
        description = {"x": ("number", "x"),
                       "y": ("number", "y")}

        data = []
                
        query = db.Query(Promising)
        filter_query = query.filter('str_values =', str_values)
        result = filter_query.get()
        point_blob = result.point_blob

        point_list = point_blob.split(',')
        del point_list[-1] # due to trailing comma
        for i in range(len(point_list)):
            if i%2 == 0:
                data.append({'x': float(point_list[i]), 'y': float(point_list[i+1])})

        data_table = gviz_api.DataTable(description)
        data_table.LoadData(data)

        logging.info(data_table.ToJSonResponse())

        self.response.out.write(data_table.ToJSonResponse())

class CreateGoodProperty(webapp.RequestHandler):
    def get(self):
        query = db.Query(Promising)
        results = query.fetch(1000)

        for result in results:
            result.good = True
            result.checked = False
            result.put()

class GraphsPage(webapp.RequestHandler):
    def get(self):
        query = db.Query(Promising)
        filter_query = query.filter('checked =', False)
        result = query.get()

        template_values = {
            'str_values': result.str_values,
            }

        directory = os.path.dirname(__file__)
        path = os.path.join(directory, '../templates/graphs_page.html')
        self.response.out.write(template.render(path, template_values))

class GoodOrBad(webapp.RequestHandler):
    def get(self):
        str_values = self.request.get('str_values')
        good = self.request.get('good_option')

        query = db.Query(Promising)
        filter_query = query.filter('str_values =', str_values)
        result = filter_query.get()

        result.good = bool(good)
        result.checked = True

        result.put()

        self.redirect('/graphs/page')

class AllOrbits(webapp.RequestHandler):
    def get(self):
        query = db.Query(Promising)
        results = query.fetch(1000)

        str_values = []

        for result in results:
            str_values.append(result.str_values)
            
        template_values = {
            'str_values': str_values,
            }

        directory = os.path.dirname(__file__)
        path = os.path.join(directory, '../templates/all-graphs.html')
        self.response.out.write(template.render(path, template_values))        

class JustGraph(webapp.RequestHandler):
    def get(self):
        str_values = self.request.get('str_values')

        query = db.Query(Promising)
        filter_query = query.filter('str_values =', str_values)
        result = filter_query.get()

        template_values = {
            'str_values': str_values,
            }

        directory = os.path.dirname(__file__)
        path = os.path.join(directory, '../templates/graphs_page.html')
        self.response.out.write(template.render(path, template_values)) 
