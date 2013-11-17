#!/usr/bin/env python2.7
import os
import time
from operator import itemgetter

def path_get_size(path):
    st = os.statvfs(path)
    free = st.f_bavail * st.f_frsize
    total = st.f_blocks * st.f_frsize
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    used_percent = 1.0
    if used != 0 and total != 0:
        used_percent = float(used)/float(total)
    return {'tot':total, 'used':used, 'free':free, 'pused': used_percent}

def files_get_info(path):
    data_ret = []
    #epoch_time = int(time.time())
    for root, dirs, files in os.walk(path):
        for name in files:
            path_name = os.path.join(path, name)
            file_size= (os.stat(path_name).st_size)
            file_mod_time= int(os.stat(path_name).st_mtime)
            data_ret.append({'name': name, 'size': file_size,
                'time_mod': file_mod_time})
    return data_ret
#dir_current = "/disk2/camera_video_backups"
#filelist = []
#time_one_day = int(60 * 60 * 24)
#data = file_get_since(dir_current, time_one_day)
#
#data = sorted(data, key=itemgetter('name', 'size'))
#for j in data:
#    print j
#
#disk_info = path_get_size(dir_current)
#print "%.2f" % disk_info['pfree']

#for root, dirs, files in os.walk(currentDir):
#    for name in files:
#        path = os.path.join(currentDir, name)
#        #print disk_info(currentDir + "/" + name)
#        file_mod_time= (os.stat(path).st_mtime)
#        epoch_time = int(time.time())
#        tt = epoch_time - time_one_day
#        if file_mod_time > tt:
#            print "name: %s size: %s" % (name, (os.stat(path).st_size))
#        # do whatever with currentfile
#disk_info("/disk2")
