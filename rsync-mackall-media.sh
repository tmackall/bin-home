#!/bin/sh
. ~/.bashrc

DEST_DIR="/backups/mackall-media"
SOURCE_DIR="/home/tmackall/"
CMD="rsync -avz --exclude-from /home/tmackall/develop/rsync-exclude.txt ${SOURCE_DIR} ${DEST_DIR}/"
echo ${CMD}
${CMD}
