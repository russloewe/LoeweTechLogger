import http.client
import base64


def getToke(url):    
    # set up header for fitbit /oauth2/token
    # <slug> is client id and client secret, see webapi /oauth/token
    b64 = '<slug>'.b64encode(code.encode('utf-8'))
    auth_header = 'Basic {}'.format(b64)
    conn = http.client.HTTPSConnection('api.fitbit.com', 443)
    conn.request('GET', url , headers={'Authorization': auth_header})
    res = conn.getresponse()
    return(res.read())
    
    
def grantUrl(host, path, args):
    url = '{}{}?'.format(host, path)
    if type(args) == type({}):
        for key in args:
            url = '{}{}={}&'.format(url, key, args[key])
        url = url.strip('&') # rm last ampersand
    url = url.strip('?')
    return(url)
  
