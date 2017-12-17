import cherrypy,zipfile, io
import redis
import os
import subprocess

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
if os.environ.get('REDIS_URL'):
    r = redis.from_url(os.environ.get("REDIS_URL"))
else:
    r = redis.StrictRedis(decode_responses=True, host='localhost', port=6379, db=0)

def redis_mass_insertion():
    ps = subprocess.Popen(('python', 'redis_commands.py'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('redis-cli', '--pipe'), stdin=ps.stdout)

def top_stocks():
    redis_mass_insertion()
    top_stocks = r.zrevrange(name='open', start=0, end=9, withscores=True )
    data = []
    for stock in top_stocks:
        data.append(r.hgetall(stock[0]))
    return data


class Root:
    @cherrypy.expose
    def index(self):
        data = top_stocks()
        tmpl = env.get_template('index.html')
        return tmpl.render(data = data)

    @cherrypy.expose
    def search(self,name):
        data = r.hgetall(name)
        tmpl = env.get_template('search.html')
        return tmpl.render(**data)

conf = {
        'global': {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': int(os.environ.get('PORT', 5000)),
        },
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './public'
        }
    }

webapp = Root()
cherrypy.quickstart(webapp, '/', conf)
