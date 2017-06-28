#!/usr/bin/python
import dropbox

accessTokenFile = open("access_token.tkn", "r")



dbx = dropbox.Dropbox(accessToken)

