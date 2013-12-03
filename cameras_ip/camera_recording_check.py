#!/usr/bin/env python2.7
'''
    checks files to make sure that they are growing. A failure
    scenario is that the cameras quit recording
'''
from cameras_info import cameras_get_info
from disk_manage import files_get_info, path_get_size
from operator import itemgetter
from libEmailTools import emailMessage
import os
import re
import sys
import time
from xml.dom import minidom, Node

#
# see how much space is available on all storage areas
def disk_get_amount_to_cleanup(info_fs):
    amount_to_cleanup = 0
    disk_percent_used = info_fs['pused']
    disk_tot = info_fs['tot']
    if disk_percent_used > info_fs['th_clean_pc']:
        amount_to_cleanup = int(disk_tot * info_fs['clean_pc'])
    return amount_to_cleanup


def main(argv):
    # camera info - read it in
    status, cam_info = cameras_get_info()

    # My code here
    fs_info = []

    # get the file system info
    index = 0
    files_unchanged = []
    status_re = re.compile("online",re.IGNORECASE)
    for i in cam_info:
        status = i['status']

        if status_re.match(status):
            dir = i['disk_location']
            number_of_cams = len(cam_info)
            file_re = ".*%s\.m.*" % i['id']
            f_re = re.compile(file_re)
            # used in file size comparison
            file_before = ""
            file_after = ""
            # get an initial snapshot of the file sizes
            file_info_first = files_get_info(dir)
            for j in sorted(file_info_first,
                    key=itemgetter('name'),
                    reverse=True):
                if f_re.match(j['name']):
                    file_before = j
                    break
            # delay some time so that the files can grow
            time.sleep(2)
            file_info_last = files_get_info(dir)
            for j in sorted(file_info_last,
                    key=itemgetter('time_mod'),
                    reverse=True):
                if j['name'] == file_before['name']:
                    file_after = j
                    break
            # list of dead camera files
            if file_before['size'] == file_after['size']:
                files_unchanged.append(file_after)
        else:
            print "%s is offline" % i['id']
    # file names - pull these out for the email text
    file_names = ""
    for k in files_unchanged:
        file_names = "%s\n%s" % (file_names, k['name'])
    if len(file_names) > 0:
        subject = "Warning: cameras may not be storing data"
        text = "Camera files:\n%s" % file_names
        emailMessage("mackall.house@gmail.com", subject, text)
    return 0

if __name__ == "__main__":
    status = main(sys.argv)
    exit(status)
