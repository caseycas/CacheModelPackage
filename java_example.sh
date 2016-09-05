#Example script to generate a cache and no cache model on the sample java data
#with trigrams
mkdir -p ./results/entropy/java/summary/
./scripts/train.py ./data/java/ 3 1.0 2
./scripts/cross.py ./data/java/ 3 -ENTROPY -BACKOFF -DEBUG -CACHE -CACHE_ORDER 3 -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES > ./results/entropy/java/3gramsCache.txt
./scripts/cross.py ./data/java/ 3 -ENTROPY -BACKOFF -DEBUG -FILES > ./results/entropy/java/3gramsNoCache.txt
python ./scripts/convertCacheResults.py ./results/entropy/java ./results/entropy/java/summary/