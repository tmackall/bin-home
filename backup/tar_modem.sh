tar --totals --exclude='apps.mbn' -zcvf $2 \
$1/AMSS/platform/l4/build_M/iguana/bin/ig_naming \
$1/AMSS/platform/l4/build_M/iguana/bin/qdms_server \
$1/AMSS/platform/l4/build_M/iguana_server/bin/ig_server \
$1/AMSS/platform/l4/build_M/kxapi/bin/quartz_servers \
$1/AMSS/platform/l4/build_M/pistachio/bin/l4kernel \
$1/AMSS/platform/l4/build_M/amss/bin/*.reloc \
$1/AMSS/platform/l4/build_M/bootimg.pbn \
$1/AMSS/products/*/build/ms/bin/ \
$1/AMSS/products/*/build/ms/*.cmm \
$1/AMSS/products/*/build/ms/*.elf \
$1/AMSS/products/*/build/ms/*.men \
$1/AMSS/products/*/build/ms/*.t32 \
$1/AMSS/products/*/drivers/hw/hwio/t32/* \
$1/AMSS/products/*/secboot/oemsbl/*.elf \
$1/AMSS/products/*/services/adsp/qdspext.h \
$1/AMSS/products/*/services/adsp/qdsprtos.h \
$1/AMSS/products/*/services/adsp/qdsprtos.c \
$1/AMSS/products/*/tools/build/ppasm.pl \
$1/AMSS/products/*/tools/debug/*.cmm \
$1/AMSS/products/*/tools/jflash/*.cmm \
$1/AMSS/products/*/tools/mjnand/jnand.elf \
$1/AMSS/products/*/tools/mjnand/*.cmm \
$1/AMSS/products/*/tools/t32/*.cmm 
