#!/usr/bin/python
import dropbox
import os
from optparse import OptionParser

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
destinationFolderName = "/" + options.destinationfolder

# Delete remote folder
if options.verbose:
    print "About to delete remote folder \"" + destinationFolderName  + "\""

try:
    dbx.files_delete(destinationFolderName)
except dropbox.exceptions.ApiError:
    if options.verbose:
        print "API error (maybe folder doesn't exist)"

# Create remote folder
if options.verbose:
    print "About to create remote folder \"" + destinationFolderName  + "\""

dbx.files_create_folder(destinationFolderName)

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