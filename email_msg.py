#!/usr/bin/env python2.7
'''
Module to send email
'''
import logging
from libPython.libEmailTools import emailMessage
from optparse import OptionParser


def read_file(file_path):
    text = ''
    # read the file in
    try:
        file_handle = open(file_path, 'r')
    except:
        logging.warning('Failed to open file: ' + file_path)
        return 1, text
    try:
        text = file_handle.read()
    except:
        logging.warning('Failed to read file: %s' % file_path)
        return 2, text
    file_handle.close()
    return 0, text


def main():
    ''' main driver
    '''
    # command-line parsing
    parser = OptionParser()
    parser.add_option('-e', help='email address',
            default='mackall.house@gmail.com')
    parser.add_option('-m', help='Message/File to email', default='')
    parser.add_option('-s', help='Email subject', default='')

    (options, _args) = parser.parse_args()

    email_address = options.e
    email_file = options.m
    email_subject = options.s
    status, email_msg = read_file(email_file)
    if status != 0:
        logging.error('Could not read file: %s', status)
        return status
    # email the message
    emailMessage(email_address, email_subject, email_msg)

    return(0)

if __name__ == "__main__":
    STATUS = main()
    exit(STATUS)
