# import the webapp module
from google.appengine.ext import webapp
# get registry, we need it to register our filter later.
register = webapp.template.create_template_register()
import urlparse
from datetime import datetime
import re
import logging
from htmlentitydefs import name2codepoint

def get_root(url):
    root = urlparse.urlparse(url).hostname
    return re.sub('w{3}\.', '', root)
    
register.filter(get_root)

def standardize_date(date):
    return date.strftime("%b %d, %Y")

register.filter(standardize_date)

def unescape(s):
    # unescape HTML code refs; c.f. http://wiki.python.org/moin/EscapingHtml
    return re.sub('&(%s);' % '|'.join(name2codepoint),
              lambda m: unichr(name2codepoint[m.group(1)]), s)

register.filter(unescape)

def list_dict(value, arg):
    return getattr(value, arg)

register.filter(list_dict)

def reddit_points(value):
    return value.ups - value.downs

register.filter(reddit_points)

def create_reddit_title_link(value):
    return 'http://reddit.com/r/' + value.subreddit + '/comments/' + value.link_id[3:]

register.filter(create_reddit_title_link)

def create_reddit_permalink(value):
    return 'http://reddit.com/r/' + value.subreddit + '/comments/' + value.link_id[3:] + '/permalink/' + value.id

register.filter(create_reddit_permalink)

def opacity(value):
    number = value/255.0
    return "%.2f" % number

register.filter(opacity)

def filter_opacity(value):
    return value*100/255

register.filter(filter_opacity)

def list_item(value, arg):
    index = int(arg)
    return value[index]

register.filter(list_item)

def colspan(value):
    value = value[0]
    if value == 1:
        return ''
    else:
        return ' colspan=' + str(value)

register.filter(colspan)

def rowspan(value):
    value = value[2]
    if value == 1:
        return ''
    else:
        return ' rowspan=' + str(value)

register.filter(rowspan)            

def transparency(value):
    value = value[3]   
    if value == 255:
        return ''
    if value == 0:
        return ' style="opacity:0;filter:alpha(opacity=0)"'
    else:
        opacity = value/255.0
        opacity_str = "%.2f" % opacity
        filter_str = str(value*100/255)
        return ' style=opacity:' + opacity_str + ';filter:alpha(opacity=' + filter_str + ')'

register.filter(transparency)

def get_tr_color(hex_color_list, table_color):
    color = hex_color_list[1]
    logging.info(table_color[9:16])
    if not color or color == table_color[10:17]:
        return ''
    else:
        return ' bgcolor="' + color + '"'
    

register.filter(get_tr_color)

def get_td_color(triple, hex_color_list):
    color = triple[-1]
    compare = hex_color_list[1]
    if color == compare:
        return ''
    else:
        return ' bgcolor="' + color + '"'

register.filter(get_td_color)

def height(hex_color_list):
    height = hex_color_list[0]
    if height == 1:
        return ''
    else:
        return ' height=' + str(height)

register.filter(height)
