#!/usr/bin/env python2.6
import smtplib
from email.mime.text import MIMEText

def emailErrors(to, subject, text):
  msg = MIMEText(text)
  msg['Subject'] = subject
  msg['From'] = "lnxbuild@localhost"
  msg['To'] = to

  s = smtplib.SMTP('smtphost.qualcomm.com')
  s.sendmail(msg['From'], msg['To'], msg.as_string())
  s.quit()

def emailMessage (to, subject, text):
  msg = MIMEText(text)
  msg['Subject'] = subject
  msg['From'] = "mackall-thomas@comcast.net"
  msg['To'] = to

  #s = smtplib.SMTP('smtphost.qualcomm.com')
  s = smtplib.SMTP('smtp.comcast.net')
  s.sendmail(msg['From'], msg['To'], msg.as_string())
  s.quit()

