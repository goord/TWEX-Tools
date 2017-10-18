#!/bin/bash

RES=${RES:-T799L91}
ERA=${ERA:-Present}
MEM=${MEM:-1}
DATE=${DATE:-20020101}
SOURCE=${SOURCE:-$PWD}
TARGET=${TARGET:-$PWD}
STARTMEM=${STARTMEM:-0}
STOPMEM=${STOPMEM:-9}
EXP=${EXP:-b0if}

CP=cp
UNZIP=gunzip
GRIB_CP=grib_copy
CDO=cdo

if [ "$SYS" == "ECMWF" ]; then
  CP=ecp
  module unload eccodes
  module load grib_api
  module load cdo
fi

function show_help {
    echo "Usage: ./copy_data.sh -r <resolution> -p <Present/Future> -m <FW-member> -d <yyyymmdd> -s <source dir> -t <target dir> -i <fc-member>"
}

OPTIND=1
while getopts "hr:p:m:d:s:t:i:" opt; do
    case "$opt" in
        h) show_help
           exit 0         ;;
        r) RES=$OPTARG    ;;
        p) ERA=$OPTARG    ;;
        m) MEM=$OPTARG    ;;
        d) DATE=$OPTARG   ;;
        s) SOURCE=$OPTARG ;;
        t) TARGET=$OPTARG ;;
        i) STARTMEM=$OPTARG && STOPMEM=$OPTARG ;;
    esac
done
shift $((OPTIND-1))
[ "$1" == "--" ] && shift

SRC=$SOURCE/$RES/$ERA/MEM${MEM}_${DATE}
TGT=$TARGET/$RES/$ERA/MEM${MEM}_${DATE}

for mem in `seq $STARTMEM $STOPMEM` ; do
  TGTDIR=$TGT/member_$mem
  echo "Creating directory $TGTDIR..."
  mkdir -p $TGTDIR
  echo "Copying gridpoint files to $TGTDIR..."
  $CP $SRC/member_$mem/ICMGG${EXP}+[0-9][0-9][0-9][0-9][0-9][0-9].gz $TGTDIR
  echo "Decompressing gridpoint files in $TGTDIR"
  for FNAME in $TGTDIR/ICMGG${EXP}+[0-9][0-9][0-9][0-9][0-9][0-9].gz ; do
    $UNZIP $FNAME
    GRIBFILE=$(echo "$FNAME" | cut -d'.' -f1)
    TMPFILE=$(mktemp $TGTDIR/ECE.XXXXXXXX)
    $GRIB_CP -w,paramId=78/79/136/137/142/143/151/164/165/166/167/186/187/188 $GRIBFILE $TMPFILE
    $CDO -f nc -z zip -t ecmwf -setgridtype,regular -aexpr,'var228=var142+var143' $TMPFILE $TGTDIR/ICMGG${EXP}.nc
    rm -f $GRIBFILE
    rm -f $TMPFILE
  done

done
