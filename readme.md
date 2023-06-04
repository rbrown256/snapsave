snapsave
===

Now updated to use Python3

# Install
```
sudo apt install pipx
pipx install pipenv
git clone https://github.com/rbrown256/snapsave
cd snapsave
pipenv install
pipenv shell
pip install dropbox
touch access_token.tkn
```

Create an App at https://www.dropbox.com/developers/apps (App folder access only) and copy/paste the access token into `access_token.tkn`.


# TODO

- This code uses long lived access tokens, which are no longer possible to be generated using Dropbox developer portal, therefore I will need to update this to use refresh tokens.
