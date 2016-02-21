import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.gen
import tornado.httpclient
import momoko
import psycopg2
import os.path
from handlers import *



settings=dict(
		template_path=os.path.join(os.path.dirname(__file__), "templates"),
		static_path=os.path.join(os.path.dirname(__file__), "static"),
		debug=True
		)

application = tornado.web.Application([
	tornado.web.url(r"/", MainHandler),
	tornado.web.url(r"/CodeChef", CodeChef),
	tornado.web.url(r"/Codeforces", CodeForces),
	tornado.web.url(r"/hackerrank", HackerRank),
	tornado.web.url(r"/query/(.*)", Query), 
	tornado.web.url(r"/db", DBHandler), ## To see the saved data
	tornado.web.url(r"/db/(.*)", DBQuery) ## To add or delete any data
	], **settings)

if __name__=="__main__":
	ioloop = tornado.ioloop.IOLoop.instance()
	application.db = momoko.Pool(
		dsn='dbname=testdb user=admin password='' host='' port=5432' ,
		size=1,
		ioloop=ioloop
		)
	future = application.db.connect()
	ioloop.add_future(future, lambda f: ioloop.stop())
	ioloop.start()
	future.result()

	server = tornado.httpserver.HTTPServer(application)
	server.listen(8888)
	print "Listening on http://127.0.0.1:8888"
	ioloop.start()
