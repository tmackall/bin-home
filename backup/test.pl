use Net::Telnet;
use strict;

use constant USER => 'root';
use constant TIMEOUT_ERROR => -1;
use constant LOGIN_ERROR => -2;
# Global Variables
my $return_code = -1;
my @command_str = '';
my @return_str = '';
my $log_filename = 'sdfsdfd.html';
my $temp_log_filename = "temp-".time."log";
my $file_line ='';
my $error_msg ='';
my $status;
my $telnet=Net::Telnet->new(Host=>"129.46.10.127", 
                            Errmode =>"return", 
                            Timeout=>60);

die "Failed to instantiate Net::Telnet(Host=>129.46.10.127): $!" unless $telnet;

# Open telnet connection to ip address
if($telnet->open("129.46.10.127") != 1)
{
   # Get error message if there is one
   $error_msg = $telnet->errmsg;
}
else
{
	sleep 1;
   # Login (no password required)
   $telnet->print(USER); 
   $status = $telnet->waitfor('/[$%#>] *$/');
   if (!$status) { 
      $error_msg="login error\n";
   } else {
   
      # Increase buffer length to 10MB
      $telnet->max_buffer_length(10485760); 

      # Start logging
      $telnet->input_log($temp_log_filename);
   
      # Issue command
      print '# ls'."\n";
      print $telnet->cmd(String=>'ls');
   
      # Get error message if there is one
      $error_msg = $telnet->errmsg;
   
      # Stop logging
      $telnet->input_log("");
   
      # Figure out return code of command
      @return_str = $telnet->cmd(String=>'echo RETURN CODE ::: $?');
      if ($return_str[$#return_str] =~ m/.*RETURN CODE ::: (.*)\n$/)
      {
         $return_code = $1;
      }
   }

   # Close telnet connection
   $telnet->close;
}

# Append/create the input log to the specified log file
if($log_filename) 
{
   # Append to log file or create a new one
   if(-e $log_filename)
   {
     open(LOG, ">>".$log_filename);
   }
   else
   {
     open(LOG, ">".$log_filename);
   }

   # Handle html logs
   if ($log_filename =~ m/.*html/) 
   {
      print LOG "\n".'<pre>'."\n";
   }

   # Print command in the log
   print LOG '# ls'."\n";

   # Output input_log to the specified log file
   open(TEMPLOG, "<".$temp_log_filename);
   while($file_line = <TEMPLOG>)
   {
      print LOG $file_line;
   }
   close TEMPLOG;

   # Print error msg in the end of the log
   if($error_msg)
   {
      print LOG "\n\n".$error_msg."\n\n";
   }

   # Handle html logs
   if ($log_filename =~ m/.*html/) 
   {
      print LOG "\n".'</pre>'."\n\n\n";
   }

   close LOG;
}

# Print input_log if command times out so we get some data to stdout
if($error_msg =~ m/.*command timed-out.*/)
{
   $return_code=TIMEOUT_ERROR;
   open(TEMPLOG, "<".$temp_log_filename);
   while($file_line = <TEMPLOG>)
   { 
      print $file_line;
   }
   close TEMPLOG;
} elsif ($error_msg) {
   print "$error_msg - some unknown error\n";
   $return_code=LOGIN_ERROR;
}

# Print error msg to stdout
print "\n\n".$error_msg;


# Exit with return code from command
exit($return_code);
