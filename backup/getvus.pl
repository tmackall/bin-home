#!/usr/local/bin/perl

use strict;
use HTTP::Date;
my $debug = 1;
my $t2=str2time(localtime);
print "$t2\n";
#my $temp=`pwd`;
#$temp=~s/.*\/(.*)$/$1/;
#my $stat=`set P4CLIENT=$temp`;
#print "stat $stat\n";

sub execute_getvu_line($)
{
  my $res = "";
  my $cmd = "";
  my $plf = 0;

  if (/^@([^\s]*)/)
  {
    # It's a label
    $cmd = "p4 sync @" . "$1,$1";
  }
  elsif (/^(\/\/.*)/)
  {
    # It's a file
    $cmd = "p4 sync $1";
  }
  elsif (/^(\/\/source.*)/)
  {
    # It's a file
    $cmd = "p4 sync $1";
  }
  elsif (/^P4Client=.*/)
  {
     #ignore the P4Client command
  }
  elsif (/^P4Port=.*/)
  {
     #ignore the P4Client command
  }
  elsif (/^\s*\/\*.*/)
  {
    # It's a comment
  }
  elsif (/^PLF=(.*)$/)
  {
    # It's a PLF
    $plf = 1;
    $cmd = "p4 sync -f $1";
  } elsif (/\s*\w+/) {
      print "ERROR - unrecognized command: $_";
  }

  if ($cmd ne "")
  {
    print "$cmd\n";

    $res = `$cmd 2>&1`;
    if (($res =~ /^Invalid changelist/) ||
        ($res =~ /not in client view/) ||
        ($res =~ /\- no such file/) )
    {
      print "ERROR in P4 command!!!\n";
      print "$res\n";
      #die $res;
    }
    else
    {
      print $res;
    }
  }

  if ($plf)
  {
    if ($res =~ /(refreshing|added as|updating) (.*)$/)
    {
      my $fd;
      open $fd, $2;
      while (<$fd>)
      {
        &execute_getvu_line($_);
      }
      close $fd;
    }
    else
    {
      print "ERROR - PLF is not present!!!\n";
      print "PLF: $_!!!\n";
      #die "$1 does not exist\n";
    }
  }
}

while (<>)
{
  &execute_getvu_line($_);
}


my $t3=str2time(localtime);
print $t3 . "\n";
print (($t3-$t2)/60) . "\n";
