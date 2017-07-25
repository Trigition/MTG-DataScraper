#!/usr/bin/env sh

if [[ "$#" < 1 ]]; then
    echo "Wrong number of parameters! Got: $#"
    echo "Primary Usage:"
    echo "\t./Gatherer_Dataminer \"[Quoted Card Set]\" [Variant Flag]"
    exit 1
fi

# Obtain Command Line Arguments
VARIANT_FLAG="false"
MAGIC_SET=$1

while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        -v|--variants)
            VARIANT_FLAG="true"
            shift
        ;;
        *)
            # Unknown input
        ;;
    esac
shift
done

DIR=$(pwd)

# Move to Crawling environment
# Prepare for data collection
cd ./mtg_dataminer 2> /dev/null
rm *.csv 2> /dev/null
rm *.out 2> /dev/null
rm *.tar.gz 2> /dev/null
mkdir -p ./images/full/"$MAGIC_SET"

echo "Web crawling for set: $MAGIC_SET"
scrapy crawl card_crawler -a card_set="$MAGIC_SET" -a variants=$VARIANT_FLAG -o "$MAGIC_SET.csv" -t csv 

echo "Finished crawling, preparing your results..."
tar -czf "$MAGIC_SET.tar.gz" images/"$MAGIC_SET"/
echo "Moving results to you"

mv *.csv $DIR
mv *.tar.gz $DIR

cd - 2> /dev/null
echo "Done!"
