#Make code suggestions
cd ./evaluation/cachemodel
make
cp suggestion ../
cd ../../

#Install mitlm
git clone https://github.com/mitlm/mitlm.git ~/mitlm
MYDIR = $PWD
cd ~/mitlm
sudo apt-get install gfortran autoconf automake libtool autoconf_archive
./autogen.sh
./configure
make
make install
cd MYDIR