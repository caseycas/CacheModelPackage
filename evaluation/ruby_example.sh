#Example script to generate a cache and no cache model on the sample ruby data
#with trigrams
mkdir -p ./results/entropy/ruby/summary
./scripts/train.py ./data/ruby/ 3 1.0 2
./scripts/cross.py ./data/ruby/ 3 -ENTROPY -BACKOFF -DEBUG -CACHE -CACHE_ORDER 3 -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES > ./results/entropy/ruby/3gramsCache.txt
./scripts/cross.py ./data/ruby/ 3 -ENTROPY -BACKOFF -DEBUG -FILES > ./results/entropy/ruby/3gramsNoCache.txt
python ./scripts/convertCacheResults.py ./results/entropy/ruby/ ./results/entropy/ruby/summary/3grams.csv