( cd tmp; ./cdpp-setup-*.sh ) # install locally
( cd tmp; ./cdpp-setup-0.4.0.sh ) # install locally
ga bin/ && gc -m sync ; make # commit and rebuild 
#1629596764
echo "The plan here is to integrate cdpath stuff with tox-py into a single tool named 'cd++' (cdpp), and use makeself.sh to install the whole thing." #
#1629637372
/c/Projects/cdpp #
#1629663777
ga bin/ && gc -m sync && make # commit and rebuild
#1629663818
docksh cdppx  # testing cdpp in docker
#1629663932
ga bin/ && gc -m sync && make && docker run --name cdppx -v `pwd`:/workarea -w /workarea --rm -it  artprod.dev.bloomberg.com/dpkg-python-development-base:3.9 bash -c 'cd tmp; ./cdpp-setup*.sh; echo Sleeping...; sleep infinity' # Testing cdpp setup
#1629664109
docker run --name cdppx -v `pwd`:/workarea -w /workarea --rm -it  artprod.dev.bloomberg.com/dpkg-python-development-base:3.9 bash -c 'cd tmp; ./cdpp-setup*.sh; echo Sleeping...; sleep infinity' # Testing cdpp setup
#1629664522
# cdpp has passed Docker smoke tests on basic functionality
#1629664999
ga bin/ && gc -m sync && make # commit and rebuild && !823
#1629668207
cdpath_add /foobar /rebar # test
#1629669654
ga bin/ && gc -m sync && make # commit and rebuild 
#1629669710
cd /c/Projects/progress-metrics.workspace/landlord # to landl
#1629670151
vimdiff ~/.local/bin/cdpp/cdpp ./  # compare with installed 
