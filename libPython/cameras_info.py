#!/usr/bin/env python2.7
'''
    lib script to encapsulate the camera info
'''
from xml.dom import minidom, Node

# what % of the file system remains before deleting files
# amount that we will cleanup relative to the filesystem total
CAMERA_XML_FILE = "/tmp/cameras.xml"


def cameras_get_info():
    '''
    cameras_get_info - reads the camera info from the XML file and
    puts it into a python data structure and returns it.
    '''
    status = 0
    xmldoc = minidom.parse(CAMERA_XML_FILE)
    itemlist = xmldoc.getElementsByTagName('camera')
    # camera info to return
    cameras_info = []
    for i in xrange(len(itemlist)):
        cameras_info.append({'id':itemlist[i].attributes['id'].value})
        a=itemlist[i].getElementsByTagName('user')
        cameras_info[i].update({'user':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('model')
        cameras_info[i].update({'model':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('passwd')
        cameras_info[i].update({'passwd':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('port')
        cameras_info[i].update({'port':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('ip_address')
        cameras_info[i].update({'ip_address':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('disk_location')
        cameras_info[i].update({'disk_location':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('mfgr')
        cameras_info[i].update({'mfgr':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('ftp_loc')
        cameras_info[i].update({'ftp_loc':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('status')
        cameras_info[i].update({'status':a[0].firstChild.data})
        a=itemlist[i].getElementsByTagName('location')
        cameras_info[i].update({'location':a[0].firstChild.data})
    return status, cameras_info

