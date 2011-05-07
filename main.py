from logic import closedorbit

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from google.appengine.dist import use_library
use_library('django', '1.2')
webapp.template.register_template_library('templatetags.templatetags')
def main():
	application = webapp.WSGIApplication([
		('/', closedorbit.MainPage),
                ('/test/starting/position', closedorbit.TestStartingPosition),
                ('/convert/to/string', closedorbit.ConvertToString),
                ('/send/calc/to/queues', closedorbit.SendCalcToQueues),
                ('/calc/points', closedorbit.CalcPoints),
                ('/return/graph/data', closedorbit.ReturnGraphData),
                ('/graphs/page', closedorbit.GraphsPage),
                ('/create/good/property', closedorbit.CreateGoodProperty),
                ('/good/or/bad', closedorbit.GoodOrBad),
                ('/all/orbits', closedorbit.AllOrbits),
                ('/just/graph', closedorbit.JustGraph),
 	],debug=True)
	util.run_wsgi_app(application)


if __name__ == '__main__':
	main()
