### Imports

from settings import *

import re, logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('nrcfeed')

from os import path

from scrape import Session, RAW

login_data = {'username': LOGIN, 'password': PASSWORD,
              'service': EPAPER_URL}

mobi_regex_compiled = re.compile(MOBI_REGEX)

def send_file(fp):
    # Import smtplib for the actual sending function
    import smtplib

    # Import the email modules we'll need
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.mime.application import MIMEApplication
    # Open a plain text file for reading.  For this example, assume that
    # Create a text/plain message
    msg = MIMEMultipart()

    # me == the sender's email address
    # you == the recipient's email address
    msg['Subject'] = 'NRC Newspaper'
    msg['From'] = SENDER_EMAIL
    msg['To'] = KINDLE_EMAIL

    attachment = MIMEApplication(fp.read(), _subtype='octet-stream')

    attachment.add_header('Content-Disposition', 'attachment', filename=path.basename(fp.name))

    msg.attach(attachment)

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP()

    s.connect(SMTP_HOST)

    if SMTP_TTLS:
        logger.debug('Starting TTLS')
        s.starttls()

    if SMTP_USERNAME:
        logger.debug('Logging into SMTP server')
        s.login(SMTP_USERNAME, SMTP_PASSWORD)

    s.sendmail(SENDER_EMAIL, [KINDLE_EMAIL], msg.as_string())
    s.quit()

### Program

s = Session()
logger.debug('Started session')

logger.debug('Logging in')
s.go(LOGIN_URL, login_data)

logger.debug(s.url)
#if s.doc.find('onjuist'):
#    logger.error('Password and/or username incorrect')
#    exit()

logger.debug('Logged in')

latest = s.doc.firsttag('a', href=mobi_regex_compiled)

latest_url = latest['href']
latest_filename = latest_url.rsplit('/', 1)[1]
logger.debug('Latest newspaper: %s' % latest_filename)

abs_path = path.join(DOWNLOAD_DIR, latest_filename)

if path.isfile(abs_path):
    logger.debug('Already downloaded, bailing off')
    
    #exit()

else:
    logger.info('Downloading newspaper')
    
    s.go(latest_url, charset=RAW)

    outfile = open(abs_path, 'wb')
    outfile.write(s.content)
    outfile.close()

logger.debug('Newspaper downloaded and written to %s', DOWNLOAD_DIR)

logger.info('Sending newsletter to %s', KINDLE_EMAIL)
infile = open(abs_path, 'rb')
send_file(infile)
infile.close()

logger.debug('Email sent to Kindle')

