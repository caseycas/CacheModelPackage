
mkdir -p results/suggestion/sample_project

# test without cache
./bin/cross.py data/sample_project 3 -BACKOFF -TEST -FILES
mkdir -p results/suggestion/sample_project/backoff.results/suggestion
cat data/sample_project/fold*.log > results/suggestion/sample_project/backoff.log
./scripts/cal_accuracy.py results/suggestion/sample_project/backoff.log > results/suggestion/sample_project/backoff.accuracy
mv data/sample_project/fold*.test.* results/suggestion/sample_project/backoff.results/suggestion


# test with file cache
./bin/cross.py data/sample_project 3 -BACKOFF -TEST -CACHE -CACHE_ORDER 10 -CACHE_DYNAMIC_LAMBDA -FILE_CACHE -FILES
mkdir -p results/suggestion/sample_project/file.cache.order10.file.dynamic.lambda.results/suggestion
cat data/sample_project/fold*.log > results/suggestion/sample_project/file.cache.order10.file.dynamic.lambda.log
./scripts/cal_accuracy.py results/suggestion/sample_project/file.cache.order10.file.dynamic.lambda.log > results/suggestion/sample_project/file.cache.order10.file.dynamic.lambda.accuracy
mv data/sample_project/fold*.test.* results/suggestion/sample_project/file.cache.order10.file.dynamic.lambda.results/suggestion


# test with window cache (window size = 5000)
./bin/cross.py data/sample_project 3 -BACKOFF -TEST -CACHE -CACHE_ORDER 10 -CACHE_DYNAMIC_LAMBDA -WINDOW_CACHE -WINDOW_SIZE 5000 -FILES
mkdir -p results/suggestion/sample_project/window.cache.order10.5000.dynamic.lambda.results/suggestion
cat data/sample_project/fold*.log > results/suggestion/sample_project/window.cache.order10.5000.dynamic.lambda.log
./scripts/cal_accuracy.py results/suggestion/sample_project/window.cache.order10.5000.dynamic.lambda.log > results/suggestion/sample_project/window.cache.order10.5000.dynamic.lambda.accuracy
mv data/sample_project/fold*.test.* results/suggestion/sample_project/window.cache.order10.5000.dynamic.lambda.results/suggestion


