from google.cloud import ndb
from googleapiclient import discovery
from googleapiclient import errors
from oauth2client import client
import flask
import google.auth
import json
import logging
import os
import requests
import requests_oauthlib

SCOPE = [
    'https://www.googleapis.com/auth/groups',
    'https://www.googleapis.com/auth/userinfo.email',
]

CLIENT_SECRETS = json.load(open('client_secrets.json'))
CLIENT_ID = CLIENT_SECRETS['web']['client_id']
CLIENT_SECRET = CLIENT_SECRETS['web']['client_secret']
AUTH_BASE_URL  = CLIENT_SECRETS['web']['auth_uri']
TOKEN_URL = CLIENT_SECRETS['web']['token_uri']

USER_AGENT = 'groupkit-app-engine/0.1'

REDIRECT_URI_PATH = '/oauth2callback'

# Arbitrary page size.
GROUPS_API = 'https://discussion.googleapis.com/v1/groups?page_size=10000'


class GroupFile(ndb.Model):
    file_id = ndb.StringProperty()
    group_email = ndb.StringProperty()

    @classmethod
    def get(cls, group_email):
        key = ndb.Key('GroupFile', group_email)
        return key.get() or cls(key=key, group_email=group_email)


def get_user_info(credentials):
    service = discovery.build('oauth2', 'v2', credentials=credentials)
    return service.userinfo().v2().me().get().execute()


def is_user_in_group(user_email, group_email, credentials):
    headers = {}
    credentials.apply(headers)
    resp = requests.get(GROUPS_API, headers=headers)
    content = resp.json()
    if 'groups' not in content:
        return False
    for group in content['groups']:
        if group.get('email') == group_email:
            return True
    return False


def is_user_in_group_via_google_drive(user_email, group_email, credentials):
    # Requires a scope such as:
    #   https://www.googleapis.com/auth/drive.readonly.metadata
    file_id = get_file_id_for_group(group_email)
    service = discovery.build('drive', 'v3', credentials=credentials)
    req = service.files().get(fileId=file_id)
    try:
        resp = req.execute()
        return True
    except errors.HttpError as e:
        if e.resp.status == 404:
            return False
        raise


def get_file_id_for_group(group_email):
    group_file = GroupFile.get(group_email)
    if group_file.file_id is not None:
        return group_file.file_id
    app_credentials = client.GoogleCredentials.get_application_default()
    scope = 'https://www.googleapis.com/auth/drive.file'
    app_credentials = app_credentials.create_scoped(scope)
    service = discovery.build('drive', 'v3', credentials=app_credentials)
    body = {'name': 'Groupkit: {}'.format(group_email)}
    req = service.files().create(body=body)
    resp = req.execute()
    file_id = resp['id']
    permission = {
	'type': 'group',
        'role': 'reader',
        'emailAddress': group_email,
    }
    req = service.permissions().create(fileId=file_id, body=permission)
    resp = req.execute()
    group_file.file_id = file_id
    group_file.put()
    return file_id


def get_token_from_environment():
    scheme = os.environ['wsgi.url_scheme']
    host = os.environ['HTTP_HOST']
    redirect_uri = '{}://{}{}'.format(scheme, host, REDIRECT_URI_PATH)
    if os.getenv('SERVER_SOFTWARE', '').startswith('Dev'):
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = True
    state = flask.session['oauth_state']
    url = flask.request.url
    google = requests_oauthlib.OAuth2Session(
            CLIENT_ID, scope=SCOPE, redirect_uri=redirect_uri)
    code = flask.request.args.get('code')
    return google.fetch_token(
            TOKEN_URL, client_secret=CLIENT_SECRET,
            code=code)
