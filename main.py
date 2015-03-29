import os
from google.appengine.ext import db
import webapp2
import jinja2
import urllib2
import requests
import random
from bs4 import BeautifulSoup
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)
    
class Employee(db.Model):
    id = db.IntegerProperty(required = True)
    name = db.StringProperty(required = True)
    role = db.StringProperty()
    date_of_joining = db.StringProperty()
    salary = db.IntegerProperty()
    current_task = db.TextProperty()
    percentage_task = db.FloatProperty()
    
"""e = Employee(id = 01, name = "Nikhil Malankar", role = "CEO",
                date_of_joining = "March 2009", salary = 20000, 
                current_task = "Monitoring the Special Ops team", percentage_task = 50.00)
e.put()"""

class Todo(db.Model):
    task = db.StringProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    
class Recieved(db.Model):
    by = db.StringProperty(required = True)
    amt = db.IntegerProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    
class Spent(db.Model):
    to = db.StringProperty(required = True)
    amt = db.IntegerProperty(required = True)
    date = db.DateTimeProperty(auto_now_add = True)
    
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        return render_str(template, **params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
class MainHandler(BlogHandler):
    def get (self, q):
        """if q is None:
            q = 'login.html'
        self.response.headers ['Content-Type'] = 'text/html'"""
        
        #Facebook likes
        s = urllib2.urlopen('http://fourtonfish.com/sitesummary/?url=https://www.facebook.com/gameeon?ref=stream&fref=nf&social=facebook')
        f = s.read()
        first_fb = f.find('facebook')
        fb = f.find('facebook', first_fb)
        start = f.find('liked": ', fb)
        end = f.find(',', start)
        fb_likes = f[start+8:end]

        #Total number of games
        games_count = 0
        url = "https://play.google.com/store/apps/developer?id=GameEon"
        req = urllib2.urlopen(url)
        src_code = req.read()
        soup = BeautifulSoup(src_code)
        for e in soup.findAll('span', {'class':'preview-overlay-container'}):
            games_count += 1
            
        #Game ratings
        game_title = []
        rating = []
        dic = {}
        grating = 0.0
        u = "https://play.google.com/store/search?q=gameeon&c=apps&hl=en"
        r = urllib2.urlopen(u)
        src = r.read()
        ss = BeautifulSoup(src)
        for e in ss.findAll('a', {'class':'title'}):
            s = e.text
            game_title.append(s)
        for e in ss.findAll('div', {'class':'current-rating'}):
            rr = e.get('style')
            rrr = rr[7:]
            arg = rrr[:-1]
            rating.append(float(arg[:-1]))
        for x,y in zip(game_title, rating):
            dic[x] = y
        for e in dic:
            if dic[e] > grating:
                grating = dic[e]
                gname = e
        summ = 0
        for e in dic:
            summ = summ + dic[e]
        avgg_rating = summ/float(games_count)
        avg_rating = int(avgg_rating)
        
        #Total number of employees
        tot_employees = Employee.all().count()
                    
        #Task percentage
        percentage_task = 0
        employees = Employee.all().fetch(50)
        for employee in employees:
            percentage_task += employee.percentage_task
        
        if percentage_task != 0 and tot_employees != 0:        
            avg_task = percentage_task/tot_employees
        
        #Notifications
        nots = Todo.all().fetch(5)
        
        #Employee names
        name = Employee.all().fetch(50)
        
        #Net revenue
        recieved = Recieved.all().fetch(100)
        rec = 0
        for e in recieved:
            rec = rec + e.amt
        spent = Spent.all().fetch(100)
        spn = 0
        for e in spent:
            spn = spn + e.amt 
        net = rec - spn           

        #Incoming revenue stats
        rec = Recieved.all().fetch(11)
        rece = []
        for e in rec:
            rece.append(int(e.amt))
            
        #Graphical representation of game ratings
        
        if avg_task:
            self.render('index.html', fb_likes = fb_likes, games_count = games_count, 
                    tot_employees = tot_employees, avg_task = avg_task, nots = nots, name = name,
                    net = net, grating = grating, gname = gname, avg_rating = avg_rating, rece = rece,
                    dic = dic)
            
        
class CalendarHandler(BlogHandler):
    def get(self):
        self.render('calendar.html')

class ToDoHandler(BlogHandler):
    def get(self):
        list = Todo.all().fetch(50)
        self.render('todo.html', list = list)
    def post(self):
        task = self.request.get("todo")
        s = Todo(task = task)
        s.put()
        list = Todo.all().fetch(50)
        self.render('todo.html', list = list)
        
class EmployeeHandler(BlogHandler):
    def get(self):
        employee = Employee.all().fetch(50)
        self.render('employees.html', employee = employee)
    def post(self):
        id = random.randrange(1, 1000)
        name = self.request.get("name")
        role = self.request.get("role")
        date_of_joining = self.request.get("date_of_joining")
        salary = int(self.request.get("salary"))
        current_task = self.request.get("current_task")
        percentage_task = float(self.request.get("percentage_task"))
        e = Employee(id = id, name = name, role = role, date_of_joining = date_of_joining,
                    salary = salary, current_task = current_task, percentage_task = percentage_task)
        e.put()
        
        self.render('employees.html', name = name, role = role, date_of_joining = date_of_joining, salary = salary, current_task = current_task)
        
class FinanceHandler(BlogHandler):
    def get(self):
        recieved = Recieved.all().fetch(50)
        spent = Spent.all().fetch(50)        
        self.render('finance.html', recieved = recieved, spent = spent)
    def post(self):
        sub = self.request.get("hidden")
        if sub == "by":
            by = self.request.get("by")
            amt = int(self.request.get("by_amt"))
            r = Recieved(by = by, amt = amt)
            r.put()
        elif sub == "to":
            to = self.request.get("to")
            amt = int(self.request.get("to_amt"))
            s = Spent(to = to, amt = amt)
            s.put()    
        recieved = Recieved.all().fetch(50)
        spent = Spent.all().fetch(50)        
        self.render('finance.html', recieved = recieved, spent = spent)    

class GameHandler(BlogHandler):
    def get(self):
        game_title = []
        rating = []
        dic = {}
        grating = 0.0
        u = "https://play.google.com/store/search?q=gameeon&c=apps&hl=en"
        r = urllib2.urlopen(u)
        src = r.read()
        ss = BeautifulSoup(src)
        for e in ss.findAll('a', {'class':'title'}):
            s = e.text
            game_title.append(s)
        for e in ss.findAll('div', {'class':'current-rating'}):
            rr = e.get('style')
            rrr = rr[7:]
            arg = rrr[:-1]
            rating.append(arg[:-1])
        for x,y in zip(game_title, rating):
            dic[x] = y
        for e in dic:
            if dic[e] > grating:
                grating = dic[e]
                gname = e
        self.render('game_stats.html', dic = dic)
        
app = webapp2.WSGIApplication([('/(.*html)?', MainHandler),
                               ('/calendar', CalendarHandler),
                               ('/todo', ToDoHandler),
                               ('/employee', EmployeeHandler),
                               ('/finance', FinanceHandler),
                               ('/game', GameHandler)],debug=True)   