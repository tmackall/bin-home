#==========================================================================
#  HEADER       ASIA Test Case Template version 1.4
#
# mo_call.sh
#
#  This is the shell script file for Voicecall test cases for targer qsd8650_surf
#==========================================================================
. $TEST_ENV_SETUP
count=1
ITERATION=$1
#after Dialng the time to get the call connected.
TIME_TO_CONNECT=8
CALL_DURATION=$2
PASS=0
PASS_COUNT=0
FAIL=1
LOG_FILE_DIR=/data
#clears the buffer.
logcat -b radio -c
#enable the screen.
sendevent /dev/input/event1 1 230 1;
sendevent /dev/input/event1 1 230 0;
sleep 1
#unlock the screen.
sendevent /dev/input/event1 1 229 1;
sendevent /dev/input/event1 1 229 0;
sleep 1
#send Select(DP-centre) Key useful for any(battery) error message.
sendevent /dev/input/event1 1 232 1;
sendevent /dev/input/event1 1 232 0;
sleep 1
#Home screen.
sendevent /dev/input/event1 1 230 1;
sendevent /dev/input/event1 1 230 0;
sleep 1
#check the phone service.
if [ `service check phone | busybox grep found | busybox wc -l` -ne 1 ]
then
	echo "Phone service is not present"
	echo "Unable to run MO call test"
	echo "MO call test case: FAIL"
	return $FAIL;
fi
#check the Radio signal.
if [ `service call phone 11 | busybox awk '/Result:/ {print $3}'` -ne 1 ]
then
	echo "Radio Signals are not present"
	echo "Please check RF cable is connected and SIM card is inserted Properly."
	echo "Did you download proper QCN file??????????"
	echo "MO call test case: FAIL"
	return $FAIL;
fi
#call the number.
service call phone 2 s16 "0123456789"
#the sleep below is required. as to open the service is taking more than 5 sec.
sleep 8
sleep $TIME_TO_CONNECT
#to check whether the call is active or not, returns 1 if call is active.
if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 1 ]
then
	#try again
	echo "$count:fist try failed, Trying again"
	sleep 8
	service call phone 2 s16 "0123456789"
	#the sleep below is required. as to open the service is taking more than 5 sec.
	sleep 8
	sleep $TIME_TO_CONNECT
	if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 1 ]
	then
		echo "$count:Call is not active"
		echo "$count:did you dial the call properly?"
		#go home :)
		sendevent /dev/input/event1 1 230 1;
		sendevent /dev/input/event1 1 230 0;
		echo "MO call test case: FAIL"
		return $FAIL;
	fi
fi
echo "$count:Call is active"
echo "the call will run for $CALL_DURATION sec"
sleep $CALL_DURATION;
#end the call
sendevent /dev/input/event2 1 107 1;
sendevent /dev/input/event2 0 0 0;
sendevent /dev/input/event2 1 107 0;
sendevent /dev/input/event2 0 0 0;
sleep $TIME_TO_CONNECT
#check the call status, returns 0 if call is not active.
if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 0 ]
then
	#try again
	echo "$count:fist try failed, Trying again"
	#end call
	service call phone 5
	sleep 4
	sleep $TIME_TO_CONNECT
	if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 0 ]
	then
		echo "$count:unable to disconnect"
		echo "$count:Call is still active"
		#go home :)
		sendevent /dev/input/event1 1 230 1;
		sendevent /dev/input/event1 1 230 0;
		echo "MO call test case: FAIL"
		return $FAIL;
	fi
fi
echo "$count:Call is disconnected"
PASS_COUNT=1
while [ $count -lt $ITERATION ];
do
	count=`expr $count + 1`
	sleep 4
	#check the Radio signal.
	if [ `service call phone 11 | busybox awk '/Result:/ {print $3}'` -ne 1 ]
	then
		sendevent /dev/input/event1 1 230 1;
		sendevent /dev/input/event1 1 230 0;
		echo "Radio Signals are not present"
		echo "MO call test case: FAIL"
		return $FAIL;
	fi
	#redial the number
	#go to dialer
	sleep 5
	sendevent /dev/input/event1 1 231 1;
	sendevent /dev/input/event1 1 231 0;
	#redial the number
	sleep 5
	sendevent /dev/input/event1 1 231 1;
	sendevent /dev/input/event1 1 231 0;
	sleep 5
	sleep $TIME_TO_CONNECT
	#check if the call is active or not returns 1 if active.
	if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 1 ]
	then
		#try again
		echo "$count:fist try failed, Trying again"
		sleep 5
		service call phone 2 s16 "0123456789"
		#the sleep below is required. as to open the service is taking more than 5 sec.
		sleep 8
		sleep $TIME_TO_CONNECT
		if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 1 ]
		then
			echo "$count:Call is not active"
			echo "$count:did you dial the call properly?"
			#go home :)
			sendevent /dev/input/event1 1 230 1;
			sendevent /dev/input/event1 1 230 0;
			echo "MO call test case: FAIL"
			return $FAIL;
		fi
	fi
	echo "$count:Call is active"
	echo "the call will run for $CALL_DURATION sec"
	#sleep for the given call duration.
	sleep $CALL_DURATION;
	#disconnect the call.
	sendevent /dev/input/event2 1 107 1;
	sendevent /dev/input/event2 0 0 0;
	sendevent /dev/input/event2 1 107 0;
	sendevent /dev/input/event2 0 0 0;
	sleep $TIME_TO_CONNECT
	#check the call status returns 0 if call is not active.
	if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 0 ]
	then
		#try again
		echo "$count:fist try failed, Trying again"
		#end call
		service call phone 5
		sleep 4
		sleep $TIME_TO_CONNECT
		if [ `service call phone 8 | busybox awk '/Result:/ {print $3}'` -ne 0 ]
		then
			echo "$count:unable to disconnect"
			echo "$count:Call is still active"
			#go home :)
			sendevent /dev/input/event1 1 230 1;
			sendevent /dev/input/event1 1 230 0;
			echo "MO call test case: FAIL"
			return $FAIL;
		fi
	fi
	echo "$count:Call is disconnected"
	PASS_COUNT=`expr $PASS_COUNT + 1`
done

#get the logs and kill logcat.
logcat -b radio -v time -f $LOG_FILE_DIR/mocall_radio_$$.log &
kill -9 `ps | busybox grep logcat | busybox awk '{ print $2 }'`
sleep 1
logcat -v time -f $LOG_FILE_DIR/mocall_time_$$.log &
kill -9 `ps | busybox grep logcat | busybox awk '{ print $2 }'`
sleep 1
logcat -b events -v time -f $LOG_FILE_DIR/mocall_events_$$.log &
kill -9 `ps | busybox grep logcat | busybox awk '{ print $2 }'`
sleep 1

#just incase the screen is left some where in the middle, to go home.
sendevent /dev/input/event1 1 230 1;
sendevent /dev/input/event1 1 230 0;

#return the status.
if [ $1 -eq $PASS_COUNT ]
then
	#return success if not find any problem. call connected.
	echo $PASS_COUNT out of $1 calls are passed
	echo "MO call test case: PASS"
	return $PASS;
else
	#return fail if not able to make the call by any reason.
	echo "MO call test case: FAIL"
	return $FAIL;
fi
