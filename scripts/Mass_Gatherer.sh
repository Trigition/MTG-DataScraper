#!/usr/bin/env sh
RED='\033[0;31m'
RESET='\033[0m'

echo "${RED}USE THIS SCRIPT ONLY WHEN NEEDED. SCRUBS ALL DEFINED SETS. BE NICE.${RESET}"
cd ..
while IFS='' read -r line || [[ -n "$line" ]]; do
    ./Gatherer_Dataminer.sh $line
done < "$1"
cd -
