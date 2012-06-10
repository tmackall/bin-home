"""
"""
import base64
import getpass
import httplib
import simplejson as json
import sys

class OmniPieBot:
    """
    """

    def __init__(self, host):
        """
          Parameters:
              host - valid omniscan host
                     production host is omniscan.qualcomm.com
                     test host is monoscan.qualcomm.com
        """
        self.host = host
        self.userpass = None
        self.baseuri = '~omniscan/publish/'

        # TODO check for valid host


    def credentials(self, typecheck, user=None, password=None):
        """
          Gets the user credentials

          Parameters
             typecheck - either 'cmdline' or 'parameter'
             user      - user name when typechek equals parameter
             password  - user password when typecheck equals parameter
        """
        if typecheck == 'cmdline':
            user = getpass.getuser()
            user = 'omnibait'
            password = getpass.getpass()
        elif not (typecheck == 'parameter'
                  and user != None
                  and password != None):
            print "Error: invalid credentials type: either 'cmdline' or 'parameter'"
            sys.exit(-1)

        self.userpass = base64.encodestring(
                   '%s:%s' % (user, password))[:-1]


    def submit(self, scanner_list, target, recipient, verify_uri=True):
        """
           Submits a scan request

           Implements scan_request/add_job

           Parameters
              scanner_list - list with the scanner strings
              target       - repository path and ID to be scanned
              recipient    - email id of the recipient to be notified
                             when scan is completed
              verify_uri   - verify the uri or not
        """
        # uri parameters
        scanner_uri = ''
        for scanner in scanner_list:
            scanner_uri += 'scan_type='+scanner+'&'

        format_uri = 'format=json&' # hardcoded

        recipient_uri = 'recipient='+recipient+'&'

        target_uri = 'fileset='+target

        fileset_uri = (self.baseuri+\
                       'scan_request/add_job?'+\
                       scanner_uri+\
                       format_uri+\
                       recipient_uri+\
                       target_uri)

        # verify valid uri
        if verify_uri == True and (not self.verify_uri(target)):
            print "Error: submit: uri is not valid"
            sys.exit(-1)

        # results
        result = self._execute(fileset_uri)

        request = json.loads(result[2:-2])

        return request

    def verify_uri(self, target):
        """
            Implementes /scan_request/verify_uri?
        """

        format_uri = 'format=json&' # hardcoded

        target_uri = 'fileset='+target

        verify_uri_str = (self.baseuri+\
                         'scan_request/verify_uri?'+\
                         format_uri+\
                         target_uri)

        result = self._execute(verify_uri_str)
        # checkk output
        try:
            data = json.loads(result[2:-2])
            return data['items'][0]['valid']
        except:
            print 'Error: verify_uri: the output is not JSON'
            print result
            sys.exit(-1)

    def status(self, submit_id):
        """
            Implements report_request/job_status?

            Parameters:
                submit_id - id of the job submitted
            Returns:

        """
        format_uri = 'format=json&' # hardcoded

        id_uri = 'id=' + str(submit_id)

        status_uri =  (self.baseuri+\
                       'report_request/job_status?'+\
                       format_uri+\
                       id_uri
               )
        result = self._execute(status_uri)
        try:
            data = json.loads(result[2:-2])

            return data['items'][0]
        except:
            print 'Error: status: the output is not JSON'
            print result
            sys.exit(-1)

    def jobs(self, target):
        """
           Implements report_request/get_jobs?

           Parameters:
                  target - target name for scan
           Returns:
                  list of jobs for target pending

        """
        format_uri = 'format=json' # hardcoded

        jobs_uri =  (self.baseuri+\
                       'report_request/get_jobs?'+\
                       format_uri)

        return_data = []

        result = self._execute(jobs_uri)
        try:
            data = json.loads(result[2:-2])
        except:
            print 'Error: status: the output is not JSON'
            print result
            sys.exit(-1)

        for entry in data['items']:
            if entry['fileset'] == target:
                return_data.append(entry)

        return return_data


    def _execute(self, uri):
        """
           Executes the HTTP request to the omniscan server

           Parameters
              uri - valid uri for omniscan
        """
        conn = httplib.HTTPSConnection(self.host)
        headers = {"Authorization":("Basic %s" % self.userpass)}
        request_string = 'https://'+self.host+'/'+uri

        try:
            req = conn.request("GET", request_string, headers=headers)
            res = conn.getresponse()
            output = res.read()
        except:
            print "Error: _execute: could not connect to server"
            sys.exit(-1)

        return output

class OmniPieBotTester:
    """
    """
    def main(self):
        """
        """
        # configuration
        omni_host = 'monoscan.qualcomm.com'

        omni_scanner_list = ['scanner:blackduck52:blackduck',
                        'scanner:idiomatic3:idiomatic']

        omni_target = 'git://git-android.quicinc.com/'+\
                      'platform/vendor/qcom-proprietary/wlan.git?'+\
                      'tag=AU_LINUX_ANDROID_GINGERBREAD.02.03.03.00.041'

        omni_recipient = 'kdegi'

        omnipie_bot = OmniPieBot(omni_host)
        omnipie_bot.credentials('cmdline')
        status = omnipie_bot.submit(omni_scanner_list,
                           omni_target,
                           omni_recipient
                          )
        print status

        status_id = status['items'][0]['id']
        status = omnipie_bot.status(status_id)

        print status

        status = omnipie_bot.jobs(omni_target)

        print status

if __name__ == "__main__":
    OmniPieBotTester().main()
    sys.exit()

