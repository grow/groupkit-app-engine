from oauth2client import client
import flask
import groupkit
import os
import requests_oauthlib

app = flask.Flask(__name__)
app.secret_key = os.urandom(24)

if os.getenv('SERVER_SOFTWARE', '').startswith('Dev'):
    app.debug = True


SCOPE = groupkit.SCOPE
CLIENT_SECRETS = groupkit.CLIENT_SECRETS
CLIENT_ID = groupkit.CLIENT_ID
CLIENT_SECRET = groupkit.CLIENT_SECRET
AUTH_BASE_URL = groupkit.AUTH_BASE_URL
TOKEN_URL = groupkit.TOKEN_URL
REDIRECT_URI = groupkit.REDIRECT_URI
USER_AGENT = groupkit.USER_AGENT


@app.route('/oauth2callback', methods=['GET'])
def callback():
    token = groupkit.get_token_from_environment()
    flask.session['oauth_token'] = token
    return flask.redirect(flask.session['oauth_callback_redirect'])


@app.route('/check')
def login():
    group_email = flask.request.args.get('group')
    flask.session['group_email'] = group_email
    if 'oauth_token' not in flask.session:
        google = requests_oauthlib.OAuth2Session(
                CLIENT_ID, scope=SCOPE, redirect_uri=REDIRECT_URI)
        authorization_url, state = google.authorization_url(
                AUTH_BASE_URL, approval_prompt='auto')  # auto, force
        flask.session['oauth_callback_redirect'] = flask.request.url
        flask.session['oauth_state'] = state
        return flask.redirect(authorization_url)
    token = flask.session['oauth_token']
    access_token = token['access_token']
    credentials = client.AccessTokenCredentials(access_token, USER_AGENT)
    user_info = groupkit.get_user_info(credentials)
    email = user_info['email']
    group = flask.session['group_email']
    result = groupkit.is_user_in_group(email, group, credentials)
    content = 'Is {} in {}? -> {}'.format(email, group, result)
    resp = flask.Response(content)
    resp.headers['Content-Type'] = 'text/plain'
    return resp


@app.route('/')
def home():
    return 'OK'
