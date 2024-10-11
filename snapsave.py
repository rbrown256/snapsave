#!/usr/bin/env python3
# Copyright (c) 2017 Rob Brown. https://markitzeroday.com/ https://twitter.com/rb256
import dropbox
import os
from optparse import OptionParser
from datetime import datetime
from functools import partial

accessTokenFile = open(os.path.dirname(os.path.realpath(__file__)) + "/access_token.tkn", "r")
accessToken = accessTokenFile.read()
accessTokenFile.close()

dbx = dropbox.Dropbox(accessToken)

parser = OptionParser()
parser.add_option("-s", "--sourcefolder", dest="sourcefolder",
                    help="Folder to save", metavar="folder")
parser.add_option("-d", "--destinationfolder", dest="destinationfolder",
                    help="Destination on Dropbox",metavar="dropbox_folder")
parser.add_option("-v", action="store_true", dest="verbose", help="Output debugging information")

(options, args) = parser.parse_args()

if options.sourcefolder is None or options.destinationfolder is None:
    parser.print_help()
    exit()

if not os.path.isdir(options.sourcefolder):
    print("Path \"" + options.sourcefolder + "\" not found.")
    exit()

# Normalise this folder 
destination_folder_name = "/" + options.destinationfolder

# Delete remote folder
if options.verbose:
    print("About to delete remote folder \"" + destination_folder_name  + "\"")

try:
    dbx.files_delete(destination_folder_name)
except dropbox.exceptions.ApiError:
    if options.verbose:
        print("API error (maybe folder doesn't exist)")

# Create remote folder
if options.verbose:
    print("About to create remote folder \"" + destination_folder_name  + "\"")

dbx.files_create_folder(destination_folder_name)

# Upload files
full_path = os.path.abspath(options.sourcefolder)

if options.verbose:
    print("About to walk local folder \"" + options.sourcefolder  + "\", parsed as \"" + full_path + "\"")

for root_o, dir_o, files_o in os.walk(full_path, True, None, False):
    
    remote_path = os.path.relpath(root_o, full_path)

    if options.verbose:
        print("Root path determined as \"" + root_o + "\"")
        print("Remote path is \"" + remote_path + "\".")

    if remote_path != ".":
        full_remote_path = "/" + options.destinationfolder + "/" + remote_path
        if options.verbose:
            print("About to create remote folder \"" + full_remote_path + "\"")
        dbx.files_create_folder(full_remote_path)
    else:
        full_remote_path = "/" + options.destinationfolder

    for file in files_o:

        local_file_path = root_o + "/" + file
        upload_path = full_remote_path + "/" + file

        if options.verbose:
            print("About to upload file \"" + local_file_path + "\" to Dropbox as \"" + upload_path + "\".")

        session_start_result = None

        chunk_size = 157286400
        offset = 0
        uploaded = False

        with open(local_file_path, "rb") as upload_file:
            # dbx.files_upload(upload_file.read(), upload_path, mute = True)
            for chunk in iter(partial(upload_file.read, chunk_size), b''):
                if not uploaded:
                    uploaded = True
                if options.verbose:
                        print("Uploading offset " + str(offset))
                if session_start_result is None:
                    if options.verbose:
                        print("Starting file")
                    session_start_result = dbx.files_upload_session_start(chunk)
                else:
                    if options.verbose:
                        print("Continuing file")
                    dbx.files_upload_session_append(chunk, session_start_result.session_id, offset)
                offset = upload_file.tell()

        upload_file.close()

        local_file_time = os.path.getmtime(local_file_path)

        if uploaded:
            if options.verbose:
                print("Finishing session")
            cursor = dropbox.files.UploadSessionCursor(session_start_result.session_id, offset)
            commit = dropbox.files.CommitInfo(upload_path, mode=dropbox.files.WriteMode('overwrite', None), autorename=False, client_modified=datetime.fromtimestamp(local_file_time), mute=False)
            dbx.files_upload_session_finish(b'', cursor, commit)
        else:
            if options.verbose:
                print("Creating empty file")
            dbx.files_upload(b'', upload_path, mode=dropbox.files.WriteMode('overwrite', None), autorename=False, client_modified=datetime.fromtimestamp(local_file_time), mute=False)
