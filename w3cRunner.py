# Author sgarrett
# for https://wiki.mozilla.org/Auto-tools/Projects/W3C_CSS_Test_Mirroring

import pdb # for development use
import os, re, hgapi, logging, shutil

def commitFile(ui, repo, **kwargs):
    '''
        commitFile runs when a file is committed. It checks
        to see if there are any test files that were committed in
        a testing directory and if there are, it commits them to the
        W3C-submitted test repository.

        See: http://danchr.bitbucket.org/mercurial-api/
        ui - a mercurial ui object
        repo - a mercurial repository object
        ***kwargs - other arguments in object style k:v
    '''
    THEFILES = repo[kwargs['node']].files()
    TESTDIR = 'mirrordir/'
    LOGEMAIL = 'auto-tools@mozilla.com'
    SENDLOG = True
    W3PATH = '/home/ctalbert/projects/testrepo/w3crepo/'
    REFTESTPATH = '/home/ctalbert/projects/testrepo/moz/reftest.list'

    test_files = filter(lambda x: re.search(TESTDIR, x) != None, THEFILES)
    if len(test_files) == 0:
        # this commit doesn't have any test files
        logging.info("No test files to upload\n")
        return
    else:
        # upload test file and reftest.list
        w3Location = hgapi.Repo(W3PATH) #W3C repo

        # add reftest.list
        shutil.copyfile(REFTESTPATH, W3PATH + "reftest.list")
        w3Location.hg_add(getFileFromFilePath(REFTESTPATH))

        # TODO: Not sure how to test if a file upload/hg_add fails
        # but when it does:
        # if SENDLOG:
        #     sendFailMail(LOGEMAIL, test_files, "the error text")

        for f in test_files:
            filename = getFileFromFilePath(f)
            # we will need to upload the file before calling hg_add()
            # using copy file for testing locally
            shutil.copyfile(f, W3PATH + filename)

            w3Location.hg_add(filename)
            logging.info("Added test file:\t" + f + "\n")

        # Committing the changes
        w3Location.hg_commit("Adding Mozilla Tests", user="me")
        logging.warn("Updated and committed test files to W3C\n")
        return


def getFileFromFilePath (s):
    return s.split('/')[-1]

def sendFailMail(toAddress, fileList, error):
    import smtplib
    from email.mime.text import MIMEText

    me = "w3cRunner.py"
    you = toAddress

    msg = MIMEText("There was an error when committing {}. Error: {}".format(
        fileList, error), 'plain')
    msg['Subject'] = 'Upload of w3c tests failed'
    msg['From'] = me
    msg['To'] = you

    server = smtplib.SMTP('localhost')
    #server.ehlo()
    #server.starttls()
    #server.ehlo()
    #server.login('username', 'password')
    server.sendmail(me, [you], msg.as_string())
    server.quit()


def haveNewTests(w3cdir, mozdir):
    '''
        This function checks if there are any
        new tests that were submitted by W3C
        that returns a bool value.

        This function also cleans up the mozilla
        testing directory.
    '''
    w3cFiles = getDirectoryListing(w3cdir)
    mozFiles = getDirectoryListing(mozdir)
    newTestCount = 0

    for f in w3cFiles:
        if f in mozFiles:
            # remove the test from css-submitted to avoid duplicate tests
            os.remove(mozdir + f)
            logging.warn(f + " removed from " + mozdir + "\n")
            # take test line from moz manifest for this file and copy it to the new manifest
            logging.info("Manifest updated for: " + f + "\n")
        else:
            # this is a new test
            newTestCount += 1
            logging.warn(f + " was added to " + w3cdir + "\n")

    return newTestCount != 0

def pushToBugzilla():
    '''
        A function that creates a bug ticket
        for testing a try run of for tests that
        were recently added.
    '''
    return

def updateRepo(location):
    repo = hgapi.Repo(location)
    repo.hg_update('')

def getDirectoryListing(directory):
    files = os.listdir(directory)
    for f in files:
        # Filtering out directories that are hidden
        if f[0] == '.':
            files.remove(f)
    return files

def main():
    '''
        This main function gets executed daily
        so that we can be updated when a new
        test is submitted/approved by W3C.
    '''
    from optparse import OptionParser

    parser = OptionParser()
    #parser.add_option('--send-log', action='store', dest='send_log',
                      #default=False, help='Boolean, for whether to send a log on fail')
    parser.add_option('--w3dir', action='store', type="string", dest='localW3CDir',
                      default='/home/ctalbert/projects/testrepo/w3crepo/',
                      help='Our local copy of the w3c approved repo.')
    parser.add_option('--mozdir', action='store', type="string", dest='mozSubmittedDir',
                      default='/home/ctalbert/projects/testrepo/moz/',
                      help='Mozilla\'s tests that are submitted to w3c.')

    (options, args) = parser.parse_args()

    #w3cSubmittedDir = 'https://hg.csswg.org/test/contributors/mozilla/submitted'
    #w3cApprovedDir = 'https://hg.csswg.org/test/approved/'

    updateRepo(options.mozSubmittedDir)
    logging.info(options.mozSubmittedDir + " updated\n")
    updateRepo(options.localW3CDir)
    logging.info(options.localW3CDir + " updated\n")

    # TODO: BUILD manfiest

    logging.info("Checking for new tests...\n")
    if haveNewTests(options.localW3CDir, options.mozSubmittedDir):
        logging.info("Yay! New tests!\n")

        # Push to Bugzilla and submit a try run
        logging.info("Pushing a bug ticket to track new test integration...\n")
        pushToBugzilla()


if __name__ == '__main__':
    main()
