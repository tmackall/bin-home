#!/usr/bin/python

from optparse import OptionParser
import requests
ON = 'on'
OFF = 'off'
URL_LIGHTS = 'http://192.168.1.18/devices/'


def main():
    # define input parameters
    parser = OptionParser()
    parser.add_option('-a', help='all of the wemo devices',
                      default=False, action='store_true')
    parser.add_option('--off', help='off flag - default is on',
                      default=False, action='store_true')
    parser.add_option('-s', help='switch name',
                      default='all')

    # read input values
    (options, args) = parser.parse_args()
    flag_on_off = ON
    if options.off:
        flag_on_off = OFF
    switch_name = options.s

    #
    # devices = get state
    r = requests.get(URL_LIGHTS)
    if r.status_code != 200:
        return(r.status_code)

    #
    # lights - output name and state
    data = r.json()
    for i in data:
        print('{}: {}'.format(i['name'], i['state']))

    #
    # light name - verify that it exists
    if switch_name is not 'all':
        flag_found = False
        for i in data:
            if i['name'] == switch_name:
                flag_found = True
                break

        if not flag_found:
            print('Could not find: {}'.format(switch_name))
            return(2)

    url = '{}{}/{}/'.format(URL_LIGHTS, switch_name, flag_on_off)
    print url
    r = requests.put(url)
    if r.status_code != 200:
        return(r.status_code)

    return 0

if __name__ == '__main__':

    status = main()
    exit(status)
