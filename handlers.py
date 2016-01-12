import tornado.web
import tornado.gen
import urllib2
import bs4
import json
import time
import socks, socket


class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('home.html'
		)

class CodeChef(tornado.web.RequestHandler):
	def get(self):
		self.render('CodeChef.html'
		)

class HackerRank(tornado.web.RequestHandler):
	def get(self):
		self.render('UnderDevelopment.html'
		)

class CodeForces(tornado.web.RequestHandler):
	def get(self):
		self.render('UnderDevelopment.html'
		)

class Query(tornado.web.RequestHandler):
	@tornado.gen.coroutine
	def get(self, path):
		h_name = self.get_argument('name')
		if path=='1':
			query = ChefQuery('ban_kar_diya')
			c_prob, p_prob = yield query.do_everything()
			
			self.render('ChefResult.html', 
					p_prob=p_prob,
					c_prob=c_prob )
			#self.write("<h2>"+str(response)+"</h2>")
			#self.finish()
		else:
			raise tornado.web.HTTPError(403)
			
class ChefQuery:
	#@classmethod
    	def __init__(self,handle_name):
        	self.handle_name = handle_name
        	self.link_list = [] 
        	self.practice_prob = []
        	self.chal_prob = {}    #dictionary of { contest name:{problems:point} }
        
	#@classmethod
        @tornado.gen.coroutine
    	def do_everything(self):
		## to connect to tor
		socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1",9050, True)
		socket.socket = socks.socksocket
		########
		url = 'https://www.codechef.com/users/%s'%self.handle_name
		print(url)
        	auth = urllib2.HTTPBasicAuthHandler()
        	opener = urllib2.build_opener(auth,urllib2.HTTPHandler )
        	urllib2.install_opener(opener)
        	link_file = urllib2.urlopen(url)
		#print(link_file.read())
        	#file_ptr = self.get_link_fileptr(url)
        	soup = bs4.BeautifulSoup( link_file.read() )
        	for link in soup.find_all('a'):
            		link_data = link.get('href')   #data is like written below
			#print(link_data)
            		if '/status/' in link_data:
	        		self.link_list.append(link_data)
		#print self.link_list
###############################################################
        	link_list = self.link_list
        	for link_data in link_list:
            		link_data = link_data.split('/')
	    		if len(link_data) == 3:
                		self.practice_prob.append( link_data[2].split(',')[0] )
            		elif len(link_data) == 4:
               			try:
                   			self.chal_prob[ link_data[1] ]
                		except KeyError:
                    			self.chal_prob[ link_data[1] ] = { link_data[3].split(',')[0]:0 }
                		else:
                    			self.chal_prob[link_data[1] ][ link_data[3].split(',')[0] ] = 0
		time.sleep(2)
		print('prac_problems' + str(self.practice_prob))
		print('chal_problems' + str(self.chal_prob))
        	print 'two done'
		return self.chal_prob, self.practice_prob
