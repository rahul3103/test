import cherrypy,zipfile, io
import redis
import os
import subprocess
import csv

from csv_downloader import get_todays_csv_file
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))

if os.environ.get('REDIS_URL'):
    r = redis.from_url(os.environ.get("REDISCLOUD_URL"))
else:
    r = redis.StrictRedis(decode_responses=True, host='localhost', port=6379, db=0)

def redis_mass_insertion():
    csv_file = get_todays_csv_file()
    with open(csv_file, 'r') as csvfile:
        csvReader = csv.reader(csvfile)
        next(csvReader)
        for row in csvReader:
            r.hmset(row[1].strip(), { 'code': row[0], 'name': row[1].strip(), 'open': row[4], 'high': row[5], 'low': row[6], 'close': row[7]})
            d = [(row[1].strip(), float(row[4]))]

            r.zadd('open', **dict(d))
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
