ga bin/ && gc -m sync && make # commit and rebuild && !823
( cd tmp; ./cdpp-setup-*.sh ) # install locally
( cd tmp; ./cdpp-setup-0.4.0.sh ) # install locally
ga bin/ && gc -m sync ; make # commit and rebuild 
( cd tmp; ./cdpp-setup-0.4.1.sh ) # install locally
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
#1629668207
cd /c/Projects/progress-metrics.workspace/landlord # to landl
#1629670151
vimdiff ~/.local/bin/cdpp/cdpp ./  # compare with installed 
#1632391730
# Added dirs() wrapper in cdpp
#1632394512
pushd /etc; pushd /usr/bin; pushd /var/log; # Add some test content to DIRSTACK for testing
#1632446795
#1632447646
echo ${#kx%c*} # Remove everything following letter 'c'
#1632449326
pushd /etc; pushd /usr/bin; pushd /var/log; pushd /etc; # Add some test content to DIRSTACK for testing
#1632449414
echo ${#1}  # Yes you can get length of positional args
#1632449909
{ oldPS1="$PS1"; unset PS1; source /c/Projects/cdpp/bin/cdpp; PS1="$oldPS1"; } # How to source cdpp from canon without reinstalling anything persistent
#1632450099
# Now dirs() is more involved: sorts the dir list, highlights the entry index keys, indicates the cwd, etc.

