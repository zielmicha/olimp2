#!/usr/bin/env python2.7
import cas_config
import Cookie
import hmac
import urllib
import urlparse
import xml.etree.ElementTree as ET

def handle(environ, start_response):
    c = Cookie.SimpleCookie()
    c.load(environ.get('HTTP_COOKIE', ''))
    try:
        username = verify_cookie(c['username'].value)
    except KeyError:
        username = None
    if not username:
        arguments = dict(urlparse.parse_qsl(environ['QUERY_STRING']))
        if 'ticket' in arguments:
            username = fetch_ticket(arguments['ticket'])
            cookie_val = set_coookie(username)
            start_response('302 Redirect', [('Set-Cookie', 'username=%s' % cookie_val),
                                            ('Location', '/?')])
            return []
        else:
            start_response('302 Redirect',
                           {'Location': cas_config.CAS_URL
                            + '/login?service='
                            + urllib.quote(cas_config.URL)}.items())

            return []

    environ['REMOTE_USER'] = username

    return cas_config.app(environ, start_response)

def fetch_ticket(ticket):
    url = '%s/serviceValidate?service=%s&ticket=%s' % (cas_config.CAS_URL,
                                                       urllib.quote(cas_config.URL),
                                                       urllib.quote(ticket))
    data = urllib.urlopen(url).read()
    tree = ET.fromstring(data)
    username = tree.find('{http://www.yale.edu/tp/cas}authenticationSuccess/'
                         '{http://www.yale.edu/tp/cas}user').text
    return username

def set_coookie(msg):
    return hmac.new(cas_config.SECRET, msg).hexdigest() + '_' + msg

def verify_cookie(cookie):
    if not cookie or '_' not in cookie:
        return None
    sign, msg = cookie.split('_', 1)
    exp_sign = hmac.new(cas_config.SECRET, msg).hexdigest()
    if exp_sign != sign:
        return None
    else:
        return msg

if __name__ == '__main__':
    import gevent
    server = gevent.pywsgi.WSGIServer(('0.0.0.0', 1234), handle)
    server.serve_forever()
