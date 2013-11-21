#!/usr/bin/env python2.7
'''
    checks files to make sure that they are growing. A failure
    scenario is that the cameras quit recording
'''
from disk_manage import files_get_info, path_get_size
from operator import itemgetter
from libEmailTools import emailMessage
import os
import sys
import time

# what % of the file system remains before deleting files
# amount that we will cleanup relative to the filesystem total
DIRS_CAMERA = [{'dir':"/disk2/camera_video_backups",
    'cameras_num':2}]

#
# see how much space is available on all storage areas
def disk_get_amount_to_cleanup(info_fs):
    amount_to_cleanup = 0
    disk_percent_used = info_fs['pused']
    disk_tot = info_fs['tot']
    if disk_percent_used > info_fs['th_clean_pc']:
        #print "%s: %.2f" % (info_fs, disk_percent_used)
        amount_to_cleanup = int(disk_tot * info_fs['clean_pc'])
    return amount_to_cleanup


def main(argv):
    # My code here
    fs_info = []

    # get the file system info
    index = 0
    for i in DIRS_CAMERA:
        dir = i['dir']
        number_of_cams = i['cameras_num']
        #
        # get an initial snapshot of the file sizes
        file_info_first = files_get_info(dir)
        file_info_first = sorted(file_info_first,
                key=itemgetter('time_mod'),
                reverse=True)
        # delay some time so that the files can grow
        time.sleep(2)
        file_info_last = files_get_info(dir)
        file_info_last = sorted(file_info_last,
                key=itemgetter('time_mod'),
                reverse=True)
        files_unchanged = []
        for j in xrange(number_of_cams):
            if file_info_last[j]['size'] == file_info_first[j]['size']:
                files_unchanged.append(file_info_last[j])
        file_names = []
        for i in files_unchanged:
            file_names.append(i['name'])
        if len(file_names) > 0:
            subject = "Warning: cameras may not be storing data"
            text = "Camera files:\n%s" % file_names
            emailMessage("mackall.tom@gmail.com", subject, text)
    return 0

if __name__ == "__main__":
    status = main(sys.argv)
    exit(status)
