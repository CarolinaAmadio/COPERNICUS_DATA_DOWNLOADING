#!/bin/bash

DATE=20240616

# da inserire e sistemare
#copernicusmarine login -username 'camadio' -password 'Bsqx3066!!'
# 
#username='camadio'
#pswrd='Bsqx3066!!'

source /g100_work/OGS23_PRACE_IT/COPERNICUS/sequence3.sh

#copernicusmarine login -username 'camadio' -password 'Bsqx3066!!'
# Check if there are .txt files in the current directory
if ls *.txt 1> /dev/null 2>&1; then
    # Remove all .txt files
    rm *.txt
    echo "Removed all .txt files"
else
    echo "No .txt files found and removed before downloading new data"
fi
mkdir -p SUPERGLIDER

#1 -->  download  files index.txt 
copernicusmarine get -i cmems_obs-ins_ibi_phybgcwav_mynrt_na_irr --index-parts -nd --force-download

rm -r index_history.txt index_monthly.txt index_platform.txt
exit 0


#2 --> filter the data per platform
grep -E "*GL_PR_GL*" index_latest.txt | cut -d ',' -f 2 | rev | cut -d '/' -f 1,2 | rev > files_to_download_all.txt

#3 --> filter the data per date 
grep $DATE files_to_download_all.txt > tmp.txt
# Check if any lines were written to the output file
if [ -s tmp.txt ]; then
    echo "Filtered lines containing date $DATE have been written to $OUTPUT_FILE."
else
    echo "No lines containing date $DATE were found in $INPUT_FILE."
fi

#4 slice the list of file for download only med   
python file_MED_download.py

copernicusmarine get --dataset-id cmems_obs-ins_ibi_phybgcwav_mynrt_na_irr --dataset-part latest --file-list files_to_download.txt --no-directories --output-directory profili --force-download --overwrite-output-data 

python build_gl_dataset.py
