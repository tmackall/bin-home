GOLDEN_LABELS=`p4 labels | grep -P 'GOLDEN_\d+_\w+BLDR_MAIN ' | grep -oP 'TIP\w+'`
CHGS=""
for label in $GOLDEN_LABELS ; do
   CHGS="`p4 changes -t -m 1 //linux/...@$label | perl -ne 'print qq|$1| if (/Change (\d+)/);'`"
   echo $label - $CHGS
done
