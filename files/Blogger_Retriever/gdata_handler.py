from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow



flow = flow_from_clientsecrets('client_secret.json',
                               scope='https://www.googleapis.com/auth/calendar',
                               redirect_uri='http://example.com/auth_return')

'''
flow = OAuth2WebServerFlow(client_id='your_client_id',
                           client_secret='your_client_secret',
                           scope='https://www.googleapis.com/auth/calendar',
                           redirect_uri='http://example.com/auth_return')
'''

auth_uri = flow.step1_get_authorize_url()
# Redirect the user to auth_uri on your platform.

credentials = flow.step2_exchange(code)