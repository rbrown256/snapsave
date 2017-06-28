#!/usr/bin/python
import dropbox
from optparse import OptionParser

accessTokenFile = open("access_token.tkn", "r")
accessToken = accessTokenFile.read()
accessTokenFile.close()

dbx = dropbox.Dropbox(accessToken)

parser = OptionParser()
parser.add_option("-f", "--sourcefolder", dest="sourcefolder",
                  help="Folder to save", metavar="folder")

(options, args) = parser.parse_args()

if options.sourcefolder is None:
    parser.print_help()