#!/usr/bin/python
import fnmatch
import getopt
import os
import re
import pprint
from cStringIO import StringIO
import subprocess
import sys
import uuid

def main(argv):

    if len(argv) < 2:
        print '    C:\\Dropbox\\EncFS P:\\'
        sys.exit(1)

    sEncFsCmd  = 'encfsctl.exe' ## @todo: Add suffix detection based on OS.
    sEncFsPwd  = ''
    sEncFSPath = sys.argv[1]
    sEncFSMount = sys.argv[2]

    ## @todo: Add language detection for non-English Dropboxes
    #sRegEx = ' \(In Konflikt stehende Kopie von.*'
    sRegEx = ' \(.*conflicted copy.*'

    ## @todo: Check existence of encrypted dir + mount.

    print 'Path: %s' % (sEncFSPath,)

    aConflicts = []
    for sRoot, aDirNames, aFilenames in os.walk(sEncFSPath):
      for sFilename in fnmatch.filter(aFilenames, '*Konf*'):
          aConflicts.append(os.path.join(sRoot, sFilename))

    pp = pprint.PrettyPrinter()

    if len(aConflicts) == 0:
        print 'No conflicts found in "%s"' % (sEncFSPath,)
    else:
        for sCurConflict in aConflicts:
            try:
                print 'Original file:\n\t%s' % (sCurConflict,)
                # Extract conflict message from encrypted file name.
                reConflictMsg = re.compile(sRegEx)
                aItems = reConflictMsg.findall(sCurConflict)
                if len(aItems) != 1:
                    raise Exception("Unable to extract conflict message")
                sConflictMsg = aItems[0]
                # Cut off conflict message.
                aItems = re.split(sRegEx, sCurConflict)
                if len(aItems) != 2:
                    raise Exception("Unable to separate conflict message from file name")
                # Cut off absolute path to get the relative one.
                aItems = aItems[0].split(sEncFSPath)
                if len(aItems) != 2:
                    raise Exception("Unable to retrieve relative file path")
                sConflictFile = aItems[1]
                sConflictPath = os.path.dirname(sConflictFile)
                # Replace backslashes with slashes, strip whitespaces.
                sConflictFile = sConflictFile.replace('\\', '/')
                sConflictFile.strip()
                print 'Encoded file:\n\t%s' % (sConflictFile,)
                # Decode the file using encfsctl.
                try:
                    procEncFSCtl = subprocess.Popen([sEncFsCmd, "decode", \
                                                     sEncFSPath, sConflictFile, \
                                                     "--extpass=" + sEncFsPwd], \
                                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    procEncFSCtlStdOut, procEncFSCtlStdErr = procEncFSCtl.communicate(input=sEncFsPwd + '\n')
                    if procEncFSCtl.returncode == 0:
                        # Only Windows: Separate output from input prompt.
                        aItems = procEncFSCtlStdOut.split("\r\n")
                        if len(aItems) != 3:
                            raise Exception("Unable to extract decoded file name")
                        sConflictFileDec = aItems[1] # + sConflictMsg[0]
                        sOrgFile = os.path.join(sEncFSMount, sConflictFileDec)
                        sOrgFileMine = sOrgFile + " " + str(uuid.uuid4());
                        print 'Org file:\n\t%s' % (sOrgFile,)
                        # Step 1: Rename the original file *directly* on the mount
                        # (to not lose its contents thru eventual IV chaining). Use
                        # a temporary name w/ an UUID.
                        os.rename(sOrgFile, sOrgFileMine)
                        print 'Decoded file:\n\t%s' % (sConflictFileDec,)
                        #print 'Re-Encoding ...'
                        procEncFSCtl = subprocess.Popen([sEncFsCmd, "encode", \
                                                         sEncFSPath, sConflictFileDec, "--extpass=" + sEncFsPwd], \
                                                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        procEncFSCtlStdOut, procEncFSCtlStdErr = procEncFSCtl.communicate(input=sEncFsPwd + '\n')
                        if procEncFSCtl.returncode == 0:
                            #pp.pprint(procEncFSCtlStdOut);
                            # Only Windows: Separate output from input prompt.
                            aItems = procEncFSCtlStdOut.split("\r\n")
                            if len(aItems) != 3:
                                raise Exception("Unable to extract re-encoded file name")
                            sConflictFileEnc = aItems[1]
                            # Append absolute path again.
                            sConflictFileEnc = os.path.join(sEncFSPath, sConflictFileEnc)
                            print 'New encoded file:\n\t%s' % (sConflictFileEnc,)
                            # Step 2: Rename the partly encoded conflict file directly
                            # on the encrypted directory to match its original file name
                            # before the conflict. This should re-enable reading its file
                            # contents again.
                            os.rename(sCurConflict, sConflictFileEnc)
                            # Step 3: Rename the same file again, this time in the mounted
                            # directory to reflect the conflicting state including the
                            # original message.
                            sOrgFileTheirs = sOrgFile + sConflictMsg
                            os.rename(sOrgFile, sOrgFileTheirs)
                            # Step 4: Rename back my file to its original file name on
                            # the mounted directory.
                            os.rename(sOrgFileMine, sOrgFile)
                    else:
                        print 'ERROR: Unable to decode file \"%s\", skipping' % (sConflictFile,)
                except OSError, e:
                    print 'ERROR: %s' % (e,)

                # Move file
            except AttributeError, e:
                print 'ERROR: %s' % (e,)

if __name__ == "__main__":
   main(sys.argv[1:])

