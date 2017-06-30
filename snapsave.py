#!/usr/bin/python
import dropbox
import os
from optparse import OptionParser
from datetime import datetime

accessTokenFile = open("access_token.tkn", "r")
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
    print "Path \"" + options.sourcefolder + "\" not found."
    exit()

# Normalise this folder 
destination_folder_name = "/" + options.destinationfolder

# Delete remote folder
if options.verbose:
    print "About to delete remote folder \"" + destination_folder_name  + "\""

try:
    dbx.files_delete(destination_folder_name)
except dropbox.exceptions.ApiError:
    if options.verbose:
        print "API error (maybe folder doesn't exist)"

# Create remote folder
if options.verbose:
    print "About to create remote folder \"" + destination_folder_name  + "\""

dbx.files_create_folder(destination_folder_name)

# Upload files
if options.verbose:
    full_path = os.path.abspath(options.sourcefolder)
    print "About to walk local folder \"" + options.sourcefolder  + "\", parsed as \"" + full_path + "\""

for root_o, dir_o, files_o in os.walk(full_path, True, None, False):
    
    remote_path = os.path.relpath(root_o, full_path)

    if options.verbose:
        print "Root path determined as \"" + root_o + "\""
        print "Remote path is \"" + remote_path + "\"."

    if remote_path != ".":
        full_remote_path = "/" + options.destinationfolder + "/" + remote_path
        if options.verbose:
            print "About to create remote folder \"" + full_remote_path + "\""
        dbx.files_create_folder(full_remote_path)
    else:
        remote_path = full_remote_path = "/" + options.destinationfolder

    for file in files_o:

        upload_path = full_path + "/" + file
        file_remote_path = full_remote_path + "/" + file

        if options.verbose:
            print "About to upload file \"" + upload_path + "\""

        upload_file = open(upload_path, "r")
        upload_file_contents = upload_file.read()
        upload_file.close()

        local_file_time = os.path.getmtime(upload_path)

        dbx.files_upload(upload_file_contents, file_remote_path, mode=dropbox.files.WriteMode('overwrite', None), autorename=False, client_modified=datetime.fromtimestamp(local_file_time), mute=False)