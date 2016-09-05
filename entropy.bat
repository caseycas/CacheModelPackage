
mkdir -p results/entropy/sample_project

# test without cache
./bin/cross.py data/sample_project 3 -ENTROPY -BACKOFF -TEST -FILES
mkdir -p results/entropy/sample_project/3grams.backoff.results
cat data/sample_project/fold*.log > results/entropy/sample_project/3grams.backoff.log
./scripts/cal_entropy.py results/entropy/sample_project/3grams.backoff.log > results/entropy/sample_project/3grams.backoff.entropy
mv data/sample_project/fold*.test.* results/entropy/sample_project/3grams.backoff.results


# test with file cache
./bin/cross.py data/sample_project 3 -ENTROPY -BACKOFF -TEST -CACHE -CACHE_ORDER 3 -CACHE_DYNAMIC_LAMBDA -FILE_CACHE -FILES
mkdir -p results/entropy/sample_project/file.cache.ngram.order.file.dynamic.lambda.results
cat data/sample_project/fold*.log > results/entropy/sample_project/file.cache.ngram.order.file.dynamic.lambda.log
./scripts/cal_entropy.py results/entropy/sample_project/file.cache.ngram.order.file.dynamic.lambda.log > results/entropy/sample_project/file.cache.ngram.order.file.dynamic.lambda.entropy
mv data/sample_project/fold*.test.* results/entropy/sample_project/file.cache.ngram.order.file.dynamic.lambda.results


# test with window cache (window size = 5000)
./bin/cross.py data/sample_project 3 -ENTROPY -BACKOFF -TEST -CACHE -CACHE_ORDER 3 -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES
mkdir -p results/entropy/sample_project/3grams.window.cache.ngram.order.5000.dynamic.lambda.results
cat data/sample_project/fold*.log > results/entropy/sample_project/3grams.window.cache.ngram.order.5000.dynamic.lambda.log
./scripts/cal_entropy.py results/entropy/sample_project/3grams.window.cache.ngram.order.5000.dynamic.lambda.log > results/entropy/sample_project/3grams.window.cache.ngram.order.5000.dynamic.lambda.entropy
mv data/sample_project/fold*.test.* results/entropy/sample_project/3grams.window.cache.ngram.order.5000.dynamic.lambda.results

