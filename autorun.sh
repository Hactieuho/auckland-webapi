#!/bin/bash
PATH=usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ISRUN=$(netstat -ln | grep :80 | wc -l)
if [[ $ISRUN -eq 1 ]]
then
  echo  $(date +"%m-%d-%y %T") "Dang hoat dong" >> /root/webapi/autorun.log
else
  cd /root/webapi
  # Execute the webapi
  screen -m -d npm run start &  
  echo  $(date +"%m-%d-%y %T") "Kich hoat lai" >> /root/webapi/autorun.log
fi
