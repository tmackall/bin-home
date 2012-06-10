#!/usr/bin/env  perl

# Task: compare two labels, create report giving
# lists of
#   only in first label
#   only in second label,
#   in both, but the revision in the label isn't same.

#
# num of calls to 'p4': 2 calls to 'p4 files'
# status: tested on Win/NT using Perl 5.6
#         tested on Darwin Mac OS X using Perl 5.8
#
# Copyright 2004 Perforce Corporation, Inc. All rights reserved.


use Getopt::Long;

my $label1 = '';
my $label2 = '';
my $debugOption = 0;
my $defaultPort = '';
my $defaultUser = '';

my $res = GetOptions ('debug|d' => \$debugOption, "port=s" => \$defaultPort,
	"user|u=s" => \$defaultUser, "label1|1=s" => \$label1,
	"label2|2=s" => \$label2);


die "--label1 XXXX must be given on command-line" if $label1 eq '';
die "--label2 XXXX must be given on command-line" if $label2 eq '';

print "label1 = $label1\n"			if $debugOption;
print "label2 = $label2\n"			if $debugOption;

#
# strategy:
#    1. We'll collect Perforce output in "label1list"
#     a.and in order to let Perl "hash/dict/assoc. array" assist,
#       we'll make an lookup hash of "label1revbyfname". Note that
#       "keys %label1revbyfname" is just the filenames in label1.
#    2. We do the same thing for "label2list".
#    3. The set-stuff has a common, 'and now we intersect...'
#       and from there, it's just printing out results.

#-----------------------------------------------------------
# first call to P4: 'p4 files @label1'
#-----------------------------------------------------------

my @label1list = readinZtag("p4 -Ztag files \@$label1");
my %label1revbyfname;
my $f;
foreach $f (@label1list) {
	my $depotFile= $f->{'depotFile'};
	my $rev = $f->{'rev'};
	$label1revbyfname{$depotFile} = $rev;
}

#-----------------------------------------------------------
# second call to P4: 'p4 files @label2'
#-----------------------------------------------------------

my @label2list = readinZtag("p4 -Ztag files \@$label2");
my %label2revbyfname;
foreach $f (@label2list) {
	my ($depotFile, $rev) = ($f->{'depotFile'}, $f->{'rev'});
	$label2revbyfname{$depotFile} = $rev;
}

# do a little set intersection/difference computation, first.

my @filesOnlyInLabel1 = ();
my @filesOnlyInLabel2 = ();
my @filesInCommon = ();

# now, to intersect the two lists.
#
# read the loop content carefully:
#		"for each thing in the first label:"
#			"if it's in the second label, also, then..."
#				add to common list
#			"otherwise...."
#				add to label1-only list
# (then the same for the other label. Note that we don't add
# to the 'common' list twice - avoids duplicate entries.)

my $fname;
foreach $fname (keys %label1revbyfname) {
	if ($label2revbyfname{$fname} > 0) {
        push(@filesInCommon, $fname);
    } else {
        push(@filesOnlyInLabel1, $fname);
    }
}
foreach $fname (keys %label2revbyfname) {
	if ($label1revbyfname{$fname} <= 0) {
        push(@filesOnlyInLabel2, $fname);
    }
}

# case 1: files in the first label but not the second

foreach $fname (@filesOnlyInLabel1) {
    print "Only in $label1:  $fname\n";
}

# case 2: files in the first label but not the second

foreach $fname (@filesOnlyInLabel2) {
    print "Only in $label2:  $fname\n";
}

# case 3: files in both labels, but different revisions
foreach $fname (@filesInCommon) {
   my $rev1 = $label1revbyfname{$fname};
   my $rev2 = $label2revbyfname{$fname};
   if ($rev1 ne $rev2) {
      print "$fname is rev $rev1 in $label1 but $rev2 in $label2\n";
   }
}

sub readinZtag
{
	my ($str) = @_;
	my (@retval);
	my ($oldIFS) = $/;

	$/ = '';		# set IFS to double-newline

	#print "running \"$str\"\n";

	open(FD, "$str|") || die "cannot run \"$str\"";
	while (<FD>) {
		my (%h);
		@fields = split("\n", $_);

		#
		# input is "... fieldname  fieldvalue",
		# so we parse it and put into assoc. array
		#
		foreach $f (@fields) {
			if ($f =~ /^\.\.\.\s+(\S+)\s+(.*)/) {
				local($key, $val) = ($1,$2);
				$h{$key} = $val;
			}
		}
		push(@retval, \%h)    if length(keys(%h)) > 0;
	}
	close(FD);

	$/ = $oldIFS;		# reset IFS
	return @retval;
}

sub readInfo {
	my ($str) = "$p4 info";
	my (%retval);

	open(FD, "$str|") || die "cannot run \"$str\"";
	while (<FD>) {
		if (/^\.\.\.\s+(\S+)\s+(.*)/) {
			local($key, $val) = ($1,$2);
			$retval{$key} = $val;
		}
	}
	close(FD);

	return %retval;
}
1;

