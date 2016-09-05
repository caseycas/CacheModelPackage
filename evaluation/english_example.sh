#Example script to generate a cache and no cache model on the sample english data
#with trigrams
mkdir -p ./results/entropy/english/summary
./scripts/train.py ./data/english/ 3 1.0 2
./scripts/cross.py ./data/english/ 3 -ENTROPY -BACKOFF -DEBUG -CACHE -CACHE_ORDER 3 -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES > ./results/entropy/english/3gramsCache.txt
./scripts/cross.py ./data/english/ 3 -ENTROPY -BACKOFF -DEBUG -FILES > ./results/entropy/english/3gramsNoCache.txt
python ./scripts/convertCacheResults.py ./results/entropy/english/ ./results/entropy/english/summary/3grams.csv