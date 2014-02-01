#!/bin/bash
#ssh -R 14028:localhost:80 tmackall@mackall-home
#ssh -nNT -R 14028:localhost:8028 mackall-home
#!/bin/bash
createTunnel() {
  /usr/bin/ssh -N -R 12028:localhost:22 mackall-home
  if [[ $? -eq 0 ]]; then
    echo Tunnel to jumpbox created successfully
  else
    echo An error occurred creating a tunnel to jumpbox. RC was $?
  fi
}
/bin/pidof ssh
if [[ $? -ne 0 ]]; then
  echo Creating new tunnel connection
  createTunnel
fi
