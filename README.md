# groupkit-app-engine

A micro utility library to check whether the current user is a member of a
Google Group. Requires the user to grant the host application access to
read metadata about files in Google Drive.

This library is currently a proof of concept and a WIP.

## Usage

1. Visit the [Google API
   Console](https://console.cloud.google.com/apis/credentials) and create a new
   OAuth client ID for a *web application*.
1. Ensure you add an authorized redirect URI for */oauth2callback*.
1. Download the secrets to `client_secrets.json`.

```
import groupkit

# Must be a user whose credentials we already have.
credentials = <credentials>
user_email = 'user@example.com'
group_email = 'group@example.com'

groupkit.is_user_in_group(user_email, group_email, credentials)
```

## Requirements

In order to check if a user is a member of a group, the group must allow members
to `View Members` and `View email addresses`.  These settings can be found under
`Manage` > `Permissions` > `Access Permissions` and should be set to `All
members of the group`.
