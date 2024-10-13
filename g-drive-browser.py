#!/bin/env python3

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


# Replace with your credentials file
SERVICE_ACCOUNT_FILE = 'gdrive.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
 scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)


def list_files(folder_id=None, show_trash=False):
    """Lists files in the specified folder, the root of the Drive, or the trash.

    Args:
      folder_id: Optional. The ID of the folder to list files from. 
                 If None, it lists files from the root of the Drive.
      show_trash: If True, lists files from the trash instead.
    """
    try:
        if show_trash:
            query = "trashed = true"
        else:
            if folder_id:
                query = f"'{folder_id}' in parents and trashed = false"
            else:
                query = "trashed = false"

        results = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name, permissions)').execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print("-" * 80)
            print("ID\tName\t\t\tPermissions\t\t\tFile ID")
            print("-" * 80)
            for i, item in enumerate(items):
                print(f"{i+1}\t{item['name'][:20]:<20}\t{item['permissions'][0]['role']}\t\t\t{item['id']}")

        return items

    except HttpError as error:
        print(f'An HTTP error occurred: {error}')
        return None
    except Exception as error:
        print(f'An error occurred: {error}')
        return None

def delete_file(file_id):
    """Deletes the file with the given file ID from Google Drive."""
    try:
        service.files().delete(fileId=file_id).execute()
        print(f'File with ID {file_id} has been deleted.')
        return True
    except HttpError as error:
        print(f'An HTTP error occurred: {error}')
        return False
    except Exception as error:
        print(f'An error occurred: {error}')
        return False

def empty_trash():
    """Empties the trash in Google Drive."""
    try:
        service.files().emptyTrash().execute()
        print('Recycle bin emptied.')
    except HttpError as error:
        print(f'An HTTP error occurred: {error}')
    except Exception as error:
        print(f'An error occurred: {error}')

def main():
    """Main function to run the Google Drive file browser."""
    while True:
        files = list_files()
        print("Trash")
        list_files(None, True)
        if files is None:
            break  # Exit if there's an error listing files

        if not files:
            print("No files found in this directory.")
        else:
            choice = input("\nEnter the ID of the file to delete, 'T' to empty trash, or Enter to exit: ")
            if choice.upper() == 'T':
                empty_trash()
            elif choice == "":
                break
            else:
                try:
                    file_index = int(choice) - 1
                    if 0 <= file_index < len(files):
                        file_id = files[file_index]['id']
                        delete_file(file_id)
                    else:
                        print("Invalid input. Please enter a valid file ID.")
                except ValueError:
                    print("Invalid input. Please enter a valid file ID or 'T'.")

if __name__ == "__main__":
    main()