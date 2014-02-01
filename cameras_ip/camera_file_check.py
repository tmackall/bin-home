#!/usr/bin/env python2.7
from disk_manage import files_get_info, path_get_size
from operator import itemgetter
from libEmailTools import emailMessage
import os
import sys

# what % of the file system remains before deleting files
# amount that we will cleanup relative to the filesystem total
DIRS_CAMERA = [{'dir':"/disk2/camera_video_backups",'th_clean_pc':0.85,
    'clean_pc':0.15},
    {'dir':"/home/tmackall/ftp/tgz-d-files", 'th_clean_pc':0.30,
        'clean_pc':1.0}]

#
# see how much space is available on all storage areas
def disk_get_amount_to_cleanup(info_fs):
    amount_to_cleanup = 0
    disk_percent_used = info_fs['pused']
    disk_tot = info_fs['tot']
    if disk_percent_used > info_fs['th_clean_pc']:
        print "%s: %.2f" % (info_fs, disk_percent_used)
        amount_to_cleanup = int(disk_tot * info_fs['clean_pc'])
    return amount_to_cleanup


def main(argv):
    # My code here
    fs_info = []

    # get the file system info
    index = 0
    for i in DIRS_CAMERA:
        dir = i['dir']
        fs_info.append(i)
        fs_info[index].update(path_get_size(dir))
        print fs_info[index]
        # get the bytes to delete based on THRESHOLD_CLEAN
        bytes_to_delete = int(disk_get_amount_to_cleanup(fs_info[index]))
        print bytes_to_delete
        #
        # cleanup?
        if bytes_to_delete > 0:
            file_info = files_get_info(dir)
            file_info = sorted(file_info, key=itemgetter('time_mod'))
            count_byte = int(0)
            files_to_delete = []
            for j in file_info:
                files_to_delete.append(j)
                count_byte += int(j['size'])
                print "%s : %s" % (bytes_to_delete, count_byte)
                if count_byte >= bytes_to_delete:
                    break
            text = ("The following files will be deleted from: %s\n" %
                    dir)
            for j in files_to_delete:
                text += "%s:%s\n" % (j['name'], j['size'])
                path_full = "%s/%s" % (dir, j['name'])
                os.remove(path_full)
            subject = ("%s has reached it''s threshold and files "
                "will be deleted. %s bytes will be deleted." %
                (dir, bytes_to_delete))
            emailMessage("mackall.tom@gmail.com", subject, text)

        index += 1
    return 0

if __name__ == "__main__":
    status = main(sys.argv)
    exit(status)
