import gevent
import gevent.monkey
import gevent.pywsgi

gevent.monkey.patch_all()

import os
import json
import cgi
import time
import yaml

import checker

events = {}

def handle(environ, start_response):
    path = environ['PATH_INFO'].strip('/')
    status, headers, data = handle0(environ,
                                    path,
                                    get_fields(environ))

    start_response('%d OK' % status,
                   headers)

    for i in data:
        yield i


def handle0(environ, path, fields):
    if not path:
        path = 'index.html'

    type = 'plain'
    if path.endswith(('.css', '.html', '.js')):
        type = path.rsplit('.', 1)[1]
        if type == 'js': type = 'javascript'

    headers = [('Content-Type', 'text/%s; charset=utf-8' % type)]

    if 'data' in fields:
        data = fields['data'].value
        task = fields['tasks'].value
        ident = begin_checking(data, task)
        return 302, [('Location', '/#' + ident)], []

    if path in os.listdir('.'):
        return 200, headers, [open(path).read()]
    elif path == 'tasks.js':
        return 200, headers, [json.dumps(get_tasks())]
    elif path.endswith('.data.js'):
        ident = path.split('.')[0]
        return 200, headers, [json.dumps(events[ident])]
    elif path.endswith('.wait.js'):
        ident, last_seen = path.split('.')[:2]
        return 200, headers, wait_for(ident, last_seen)
    else:
        return 404, headers, []

def wait_for(ident, last_seen):
    last_seen = int(last_seen)
    for i in xrange(20):
        if len(events[ident]) != last_seen:
            break
        time.sleep(0.3)

    return [json.dumps(events[ident])]

def get_fields(environ):
    return cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ)

def get_tasks():
    l = []
    for name in os.listdir('.'):
        if name.startswith('task_'):
            name = name[5:]
            l.append((name, get_title(name)))
    return l

def get_title(name, _cache={}):
    if name not in _cache:
        _cache[name] = yaml.safe_load(open('task_%s/def.yaml' % name)).get('name', name)
    return _cache[name]


def begin_checking(data, task):
    ident = os.urandom(10).encode('hex')
    out_list = []
    events[ident] = out_list
    gevent.spawn(lambda: checker.check(task, data, out_list.append))
    return ident

if __name__ == '__main__':
    server = gevent.pywsgi.WSGIServer(('0.0.0.0', 1234), handle)
    server.serve_forever()
