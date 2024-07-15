#!/bin/bash

DATE=20240616
TMP1=GL_Last30_GL.txt # in the GLobal dataset (GL_) last 30 days (Last30) OF gLIDER DATA (GL)

# da inserire e sistemare
#copernicusmarine login -username 'camadio' -password 'Bsqx3066!!'
#username='camadio'
#pswrd='Bsqx3066!!'

source /g100_work/OGS23_PRACE_IT/COPERNICUS/sequence3.sh

#################################################### Start ##################################################
echo "....Starting program..."
echo ""
echo ""


# Check if there are .txt files in the current directory
if ls *.txt 1> /dev/null 2>&1; then
    # Remove all .txt files
    rm *.txt
    #echo "Removed all .txt files"
else
    echo ""	
    #echo "No .txt files found and removed before downloading new data"
fi
mkdir -p SUPERGLIDER

#1 -->  download  files index.txt 
echo "... Downloading index_latest"
echo ""
echo ""
copernicusmarine get -i cmems_obs-ins_ibi_phybgcwav_mynrt_na_irr --index-parts -nd --force-download
shopt -s extglob
echo ""
echo ""
echo "...done"

if [ -s index_latest.txt ]; then
    echo "" #"all other *.txt files will be removed"
    rm -r index_history.txt index_monthly.txt index_platform.txt
else
    # Capture the line number where the error occurs
    LINENO_STR="Error occurred in line ${LINENO}"
    echo "${LINENO_STR}"
    exit 0
fi


#2 --> filter the data per platform
echo ""
echo ""
echo "... Selecting only gliders data"
grep -E "*GL_PR_GL*" index_latest.txt | cut -d ',' -f 2 | rev | cut -d '/' -f 1,2 | rev > $TMP1 
echo ""
echo "... done"
echo ""

#3 --> filter the data per date 
grep $DATE $TMP1 > tmp.txt
# Check if any lines were written to the output file
if [ -s tmp.txt ]; then
    echo "Filtered lines containing date $DATE have been written to $OUTPUT_FILE as tmp.txt"
else
    echo "No lines containing date $DATE were found in $INPUT_FILE."
fi

echo ""
echo ""


#4 slice the list of file for download only med   
echo ""
echo ""
echo "... Starting selecting Mediterranean only... "
echo ""
python Select_Mediterranean_domain.py
echo ""
echo ""

copernicusmarine get --dataset-id cmems_obs-ins_ibi_phybgcwav_mynrt_na_irr --dataset-part latest --file-list files_to_download.txt --no-directories --output-directory profiles --force-download --overwrite-output-data 

exit 0

python build_gl_dataset.py
