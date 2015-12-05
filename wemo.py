#!/usr/bin/python

from optparse import OptionParser
from ouimeaux.environment import Environment
from json import dumps
ON = 1
OFF = 0

def switch_set(env, list_switches, val_on_off):
    '''
    switch_set - turns the wemo switch either on or off. Will
    execute for all the switches in the list
    '''

    for switch in list_switches:
        s = env.get_switch(switch)
        s.basicevent.SetBinaryState(BinaryState=val_on_off)

def switch_get(env, list_switches):
    '''
    switch_get - returns the state of the switch
    '''
    ret_list = []
    for switch in list_switches:
        s = env.get_switch(switch)
        state = s.basicevent.GetBinaryState()
        state = int(state['BinaryState']) & 0x9
        if state > 0:
            state = 1
        ret_list.append({switch: state})

    return ret_list


def main():
    # define input parameters
    parser = OptionParser()
    parser.add_option('-a', help='all of the wemo devices',
                      default=False, action='store_true')
    parser.add_option('-g', help='get switch state',
                      default=False, action='store_true')
    parser.add_option('-l', help='list all the switches',
                      default=False, action='store_true')
    parser.add_option('--off', help='off flag - default is on',
                      default=False, action='store_true')
    parser.add_option('-s', help='switch name',
                      default=None)


    # read input values
    (options, args) = parser.parse_args()
    flag_on_off = ON
    if options.off:
        flag_on_off = OFF
    flag_list = options.l
    flag_get = options.g
    switch_name = options.s

    #
    # environment - wemo
    env = Environment()
    env.start()
    env.discover()
    switches = env.list_switches()

    if switch_name is not None:
        if switch_name not in switches:
            print '%s is not available' % switch_name
            return {'status': 1}
        else:
            switches = [switch_name]

    if flag_list:
        return {'status': 0, 'msg': switches}

    if flag_get:
        return {'status': 0, 'msg': switch_get(env, switches)}

    #
    # switch - on/off
    print switches
    switch_set(env, switches, flag_on_off)
    return {'status': 0, 'msg': 'switch(es):%s val:%s' % (switches, flag_on_off)}

if __name__ == '__main__':
    status = main()
    if status['status'] == 0:
        dumps(status)
    exit(status)

