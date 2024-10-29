snapsave
===

Python scripts to backup files and folders to Dropbox/Google Drive.

# Example Usage

Make a script like so:

```
#!/bin/bash
set -e
mkdir -p /var/tmp/snapsave
rm /var/tmp/snapsave/* || true

tar -cvf - --exclude=/boot --exclude=/proc  --exclude=/sys  --exclude=/tmp  --exclude=/run \
 --exclude=/mnt  --exclude=/media  --exclude=/dev  --exclude=/lost+found --exclude=/var/tmp / | \
 pigz | gpg -e -r you@example.com --trust-model always -o /var/tmp/snapsave/web-server.tar.gz.gpg

# Backup to Dropbox
/root/.local/share/virtualenvs/snapsave-jmkwb-WP/bin/python /opt/snapsave/snapsave.py \
 -s /var/tmp/snapsave/ -d dropbox_directory

# Backup to Google Drive
/root/.local/share/virtualenvs/snapsave-jmkwb-WP/bin/python /opt/snapsave/snapsave-g-drive.py \ 
 -s /var/tmp/snapsave/web-server.tar.gz.gpg -d cokv1agzzrlkp5roq7bfug6bl04jvq51xe
```

Schedule this using `crontab -e`:

`5 5 * * 1 /opt/snapsave/backup.sh >> /var/log/snapsave.log`

# Updates

- 2024-10-12: Added Google Drive script
- 2023-06-04: Updated to use Python3

# Install
```
sudo apt install pipx
pipx ensurepath
bash
pipx install pipenv
git clone https://github.com/rbrown256/snapsave
cd snapsave
pipenv install
pipenv shell
touch access_token.tkn gdrive.json
```
## Google Drive

The `gdrive.json` file contains the authentication credentials your application needs to access the Google Drive API.
snapsave will use a service account that you setup. It will only have permission to access the folder you share with your service account.

Follow these steps to create it:

**1. Set up a Service Account**

*   Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
*   Create a new project.
*   Ensure you have selected the correct project.
*   Go to **IAM & Admin > Service Accounts**.
*   Click **CREATE SERVICE ACCOUNT**.
*   Provide a name and optional description for your service account.
*   Click **CREATE AND CONTINUE**.

**2. Grant Necessary Permissions**

*   Under **Grant this service account access to project**, click **Select a role**.
*   Search for "Drive" and select **Basic > Editor**. This role allows the service account to upload files to Google Drive.
*   Click **CONTINUE**.

**3. (Optional) Grant User Access**

*   If needed, grant access to this service account to other users. 
*   Click **DONE**.

**4. Create a Key**

*   Locate your newly created service account in the list and click on it.
*   Go to the **KEYS** tab.
*   Click **ADD KEY > Create new key**.
*   Select **JSON** as the key type.
*   Click **CREATE**.

    **Important:** A JSON file containing your key will be downloaded. This is your `gdrive.json` file. Store it securely, as this is the only copy of this key. If lost, you will need to generate a new one.

**5.  Set folder permissions:**

As your service account will only have the default 15GB available to it (this is separate from your Google account), it is recommended to regularly move files shared with the service account to your
own Google Drive. This will allow new uploads using Snapsave to successfully complete. This assumes you have more than the 15GB default available in your own Drive account.

Recommended folder structure:

```
Google-Drive-Root
    Snapsave
      Inbox
      Archive
```

Use [this Google Apps Script](https://gist.github.com/rbrown256/ff5b38058f3e53c59018a9dcbb50e80d) to regularly move files from `Inbox` to `Archive`, which will take ownership and return the quota to the service account:

`copyAndDeleteFiles('<ID of Inbox>', '<ID of Archive>');`

To find the ID navigate to the folder in the Web UI for Google Drive and check the URL: e.g. `https://drive.google.com/drive/folders/cokv1agzzrlkp5roq7bfug6bl04jvq51xe` gives the ID as `cokv1agzzrlkp5roq7bfug6bl04jvq51xe`.

In [Google Apps Script](https://script.google.com/) click `New Project` then simply paste in the script from above. Set `main` to trigger e.g. every 15 minutes after adding your IDs to the `main()` function.

* **In Google Drive, locate the specific folder you want your service account to access.**
* Right-click on the folder (`Inbox` in the example above) and select "Share".
* In the "Share with people and groups" field, **enter the email address of your service account.** (You can find this email address on the Service Accounts page in the Cloud Console.)
* **Choose the appropriate role:**
    * **Editor:**  Allows viewing, commenting, editing, and organizing files within the folder.
* Click "Send".
* You will pass the ID of this folder (or one within it) to `snapsave-g-drive.py` using the `-d` parameter.
* To find the ID navigate to the folder in the Web UI for Google Drive and check the URL: e.g. `https://drive.google.com/drive/folders/cokv1agzzrlkp5roq7bfug6bl04jvq51xe`
* In this case, the ID is `cokv1agzzrlkp5roq7bfug6bl04jvq51xe`

**6. Use the Credentials File**

*   Place the `gdrive.json` file in the Github project directory.

**Security Best Practices**

*   **Principle of Least Privilege:** Grant only the necessary permissions (roles) to your service account.
*   **Secure Storage:** Store your `gdrive.json` file securely. Consider using environment variables or secret management services in production environments.
*   **Rotation:** Regularly rotate your service account keys to minimize security risks.

Note that `g-drive-browser.py` is provided to allow the Google Drive of the service account to be inspected, and files deleted. Simply run `g-drive-browser.py` with no args and it logs into
Google Drive as the service account specified in `gdrive.json`.

## Dropbox

Create an App at https://www.dropbox.com/developers/apps (App folder access only) and copy/paste the access token into `access_token.tkn`. As of 2024-04-21 it is still possible to create access tokens for your own account:

> By generating an access token, you will be able to make API calls for your own account without going through the authorization flow. To obtain access tokens for other users, use the standard OAuth flow.

Do this from the settings page from your app on Dropbox. e.g. `https://www.dropbox.com/developers/apps/info/[App Key]#settings`
