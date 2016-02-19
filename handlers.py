import tornado.web
import tornado.gen
import urllib2
import bs4
import json
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
		self.render('CodeForces.html'
		)

class Query(tornado.web.RequestHandler):
	@tornado.gen.coroutine
	def get(self, path):
		h_name = self.get_argument('name')
		if path=='1':
			query = ChefQuery(h_name)
			c_prob, p_prob = yield query.do_everything()
			
			self.render('ChefResult.html', 
					p_prob=p_prob,
					c_prob=c_prob )
		elif path=='2':
			query = ForcesQuery(h_name)
			prob = yield query.do_everything()
			c_prob = []
			p_prob = []
			for key in prob.keys():
				if prob[key]["prac/cont"]=='CONTESTANT':
					c_prob.append(prob[key])
				else:
					p_prob.append(prob[key])
			self.render('ForcesResult.html', 						p_prob=p_prob, 
					c_prob=c_prob)
		else:
			raise tornado.web.HTTPError(403)
			
class ChefQuery:
    	def __init__(self,handle_name):
        	self.handle_name = handle_name
        	self.link_list = [] 
        	self.practice_prob = []
        	self.chal_prob = {}    #dictionary of { contest name:{problems:point} }
        
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
        	soup = bs4.BeautifulSoup( link_file.read() )
        	for link in soup.find_all('a'):
            		link_data = link.get('href')   #data is like written below
            		if '/status/' in link_data:
	        		self.link_list.append(link_data)
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
		for link in self.link_list:
            		if len( link.split('/') )  == 4 :
                		url = 'https://www.codechef.com' + link
				print url
				link_file = urllib2.urlopen(url)
                		soup = bs4.BeautifulSoup( link_file.read() )
                		a = soup.findAll('td',{'class':'centered','width':'51'})
                		max_points = 0
                		for i in a:
                    			points= i.findAll(text=True)
                    			if len(points) == 2 :
                        			if points[0] > max_points :
                           				max_points = points[0]
                    			if points==[] :
                        			max_points = 100
                		link_data = link.split('/')
                		self.chal_prob[ link_data[1] ][ link_data[3].split(',')[0] ] = max_points
		print('prac_problems' + str(self.practice_prob))
		print('chal_problems' + str(self.chal_prob))
		return self.chal_prob, self.practice_prob

class ForcesQuery:
    def __init__(self,handle_name):
        self.handle_name = handle_name
        self.rating_url = 'http://codeforces.com/api/user.rating?handle=%s'%self.handle_name
        self.prob_url = 'http://codeforces.com/api/user.status?handle=%s'%self.handle_name
        self.all_contest_url = 'http://codeforces.com/api/contest.list'
        
        self.chall_prob = {}        #a dictionary of { (contest_id,index) : list }
                                    #each element of the list contains a list containing prob. name,maxmum points obtainable,points obtained ,practice/contest
                                    #of solved problems
        self.contest_rating = []    #contains a list of tuple of contest_id,contest name and
                                    #its rating in that contest.
        self.contest_timing = {}
        self.list_of_contest = []
        
    @tornado.gen.coroutine 
    def do_everything(self):
	socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1",9050, True)
	socket.socket = socks.socksocket
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(auth,urllib2.HTTPHandler )
        urllib2.install_opener(opener)
  
        link_file = urllib2.urlopen(self.prob_url)
        data = link_file.read()
        data = json.loads(data)
        if data['status'] != "OK" :
            print data['comment']
        else:
            print 'OK'
            for i in data['result']:
                if i['verdict'] == "OK" or i['verdict'] == "PARTIAL" :
                    if i['contestId'] not in self.list_of_contest and i['author']['participantType'] == "CONTESTANT" :
                        self.list_of_contest.append(i['contestId'])
                    try:
                        i['problem']['points']
                    except KeyError:
                        self.chall_prob[ (i['contestId'],i['problem']['index']) ] =  { 'name' : i['problem']['name'],'prac/cont': i['author']['participantType'] } 
                    else:
                        self.chall_prob[ (i['contestId'],i['problem']['index']) ] =  { 'name' : i['problem']['name'],'total_points' : i['problem']['points'],'prac/cont': i['author']['participantType'] }
                            
        for i in self.list_of_contest:           # i is a contest_id
            url = 'http://codeforces.com/api/contest.standings?contestId=%d&handles=%s'%(i,self.handle_name)
            link_file = urllib2.urlopen(url)
            data = link_file.read()
            data = json.loads(data)
            number_of_ques = len(data['result']['rows'][0]['problemResults'])
            for j in range( number_of_ques ):
                try :
                    self.chall_prob[ (i,data['result']['problems'][j]['index']) ]
                except KeyError :
                    continue
                else:
                    self.chall_prob[ (i,data['result']['problems'][j]['index']) ]['actual_points'] = data['result']['rows'][0]['problemResults'][j]['points']
        print 'second done'
	
	#gives rating of all participated contests
        link_file = urllib2.urlopen(self.rating_url)
        data = link_file.read()
        data = json.loads(data)
        if data['status'] != 'OK':
            print data['comment']
        else:
            for i in data['result']:
                self.contest_rating.append((i['contestId'],i['contestName'],i['newRating']))
	self.chall_prob = {str(key):value for key,value in self.chall_prob.items() }
        print 'last done'
	return self.chall_prob
  
    def contest_timing_(self):                                   #may be useful , but not used now.
        link_file = self.get_link_fileptr( self.all_contest_url )
        data = link_file.read()
        data = json.loads(data)
        if data['status'] != 'OK' :
            print data['comment']      #change has to be made here  i think its comment
        else:
            for i in data['result']:
                self.contest_timing[ i['id'] ] = i['startTimeSeconds'] + i['durationSeconds']  #has info abount when the contest ended.
