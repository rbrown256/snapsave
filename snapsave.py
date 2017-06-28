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

if os.path.isdir(options.sourcefolder):
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
else:
    print "Path \"" + options.sourcefolder + "\" not found."