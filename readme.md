snapsave
===

Python script to backup files and folders to Dropbox.

# Example Usage

Make a script like so:

```
#!/bin/bash
mkdir -p /var/tmp/snapsave
rm /var/tmp/snapsave/*.7z
7za a -x'!var/tmp/snapsave' -mhe=on -p'secret-password' /var/tmp/snapsave/server.7z /opt /etc /home /root /var
/root/.local/share/virtualenvs/snapsave-jmkwb-WP/bin/python /opt/snapsave/snapsave.py -s /var/tmp/snapsave/ -d my-server
rm /var/tmp/snapsave/*.7z
```

Schedule this using `crontab -e`:

`5 5 * * 1 /opt/snapsave/backup.sh >> /var/log/snapsave.log`

# Updates

- 2023-06-04: Updated to use Python3

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
