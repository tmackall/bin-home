#!/usr/bin/zsh

P4PORT=qctp410:1666

for f in `p4 files //linux/target/\*/main/binary/... |
                grep -v delete | sed -e 's|#.*$||'` ; do
   rev=`p4 changes $f | grep -oP 'Integrate \w+' |
           head -1 | sed -e 's|Integrate ||'`
   target=`echo $f | grep -oP '/target/\w+/' | sed -e 's|/||g' -e 's|target||'`
   echo $f | grep -q -e -ff
   if [ $? != 0 ] ; then
      tlen=`echo $target | wc -c`
      wslen=`echo "11 - $tlen" | bc`
      ws=`perl -e "print ' ' x $wslen"`
      echo "$target$ws$rev"
   fi
done

