#!/usr/bin/env python3

import argparse
import mimetypes
import os
import time

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Replace with your credentials file
SERVICE_ACCOUNT_FILE = 'gdrive.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

def delete_all_files(folder_id=None):
    """Deletes all files in the specified folder or the entire Drive.
    
    Args:
      folder_id: Optional. The ID of the folder to delete files from. 
                 If None, it deletes all files in the entire Drive.
    """
    try:
        # If folder_id is provided, list files only from that folder
        if folder_id:
            query = f"'{folder_id}' in parents and trashed = false"
        else:
            query = "trashed = false"

        # List files in the Drive
        results = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)').execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')

        else:
            print('Deleting files:')
            for item in items:
                file_id = item['id']
                service.files().delete(fileId=file_id).execute()
                print(f'{item["name"]} ({item["id"]}) deleted.')

        # Empty the recycle bin
        service.files().emptyTrash().execute()
        print('Recycle bin emptied.')

    except HttpError as error:
        print(f'An HTTP error occurred: {error}')
    except Exception as error:
        print(f'An error occurred: {error}')

def upload_and_replace(source_file, destination_folder_id):
    """Uploads a file to Google Drive, replacing any existing file with the same name.

    Args:
      source_file: The path to the file on your local machine.
      destination_folder_id: The ID of the Google Drive folder to upload to.
    """
    try:
        print("Starting upload process...")  # Log the start of the process

        # Check if the file already exists in the destination folder
        filename = os.path.basename(source_file)
        query = f"name='{filename}' and '{destination_folder_id}' in parents and trashed = false"
        print(f"Querying for existing files: {query}")  # Log the query
        results = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name)').execute()
        items = results.get('files', [])

        # Delete existing file if found
        if items:
            file_id = items[0]['id']
            service.files().delete(fileId=file_id).execute()
            print(f'Existing file with ID {file_id} has been deleted.')

        # Give time for server-side to reallocate quota
        time.sleep(60)

        # Upload the file
        mimetype = mimetypes.guess_type(source_file)[0]
        file_metadata = {'name': filename, 'parents': [destination_folder_id]}
        media = MediaFileUpload(source_file, mimetype=mimetype, resumable=True)
        print("Uploading the file...")  # Log before uploading
        file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
        print(f'File uploaded with ID: {file.get("id")}')

    except HttpError as error:
        print(f'An HTTP error occurred: {error}')
        # More detailed error handling (e.g., check error.resp.status)
    except Exception as error:
        print(f'An error occurred: {error}')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload and replace a file in Google Drive.')
    parser.add_argument('-s', '--source_file', required=True, help='Path to the source file')
    parser.add_argument('-d', '--destination_folder_id', required=True, help='ID of the destination folder in Google Drive')
    args = parser.parse_args()

    delete_all_files()
    upload_and_replace(args.source_file, args.destination_folder_id)
