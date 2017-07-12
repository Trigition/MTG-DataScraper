#!/usr/bin/env sh

if [[ "$#" -ne 1 ]]; then
    echo "Wrong number of parameters!"
    echo "Usage:"
    echo "\t./Gatherer_Dataminer \"[Quoted Card Set]\""
    exit 1
fi

MAGIC_SET=$1
DIR=$(pwd)

# Move to Crawling environment
# Prepare for data collection
cd ./mtg_dataminer 2> /dev/null
rm *.csv 2> /dev/null
rm *.out 2> /dev/null
rm *.tar.gz 2> /dev/null

echo "Web crawling for set: $MAGIC_SET"
scrapy crawl card_crawler -a card_set="$1" -o "$1.csv" -t csv

echo "Finished crawling, preparing your results..."
tar -czf "$1.tar.gz" images/full/
echo "Moving results to you"

mv *.csv $DIR
mv *.tar.gz $DIR

cd - 2> /dev/null
echo "Done!"
