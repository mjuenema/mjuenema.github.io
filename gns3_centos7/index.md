## Installing GNS3 on CentOS 7

I originally wrote this article in August 2017. I retained the original version but
would like to make two comments.

1. In my view, [EVE-NG](https://www.eve-ng.net/) would be a better choice than [GNS 3](https://www.gns3.com/]) now.
2. It would be better to install the Python packages and other software into `~/.local` instead of `/usr/local/`.

-----

GNS3 is a popular network software emulator. It uses the Dynamips emulation software to 
simulate Cisco IOS. The official documentation includes installation guides for Ubuntu, 
Debian, Arch Linux, Fedora and OpenSuse. This article explains how to install GNS3 on CentOS 7.
Requirements

GNS3 is written in Python 3, Python 2 is not supported. The Python 3 packages are not 
available through the CentOS RPM repositories but they are available on EPEL. The steps 
below add the EPEL repository, install Python 3.4, QT5 and various other packages that 
are either needed or are useful for running GNS3.

```
sudo yum install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
sudo yum install python34 python34-devel python34-setuptools python34-tools
sudo yum install elfutils-libelf-devel libpcap-devel cmake glibc-static qemu telnet gnome-terminal putty
sudo yum install qt5-qtbase qt5-qtbase-devel qt5-qtsvg qt5-qtsvg-devel
sudo yum groupinstall Fonts
curl https://bootstrap.pypa.io/get-pip.py | sudo python3.4
```

### GNS3

Once Python 3.4 has been installed, the latest GNS3 releases are available from PyPi and are easily installed through the pip3.4 script.

```
sudo pip3.4 install gns3-server gns3-gui
```

### Qt5 and Python 3 bindings

GNS3 relies on the Python 3 bindings for the QT5 toolkit. These are not available for CentOS 7 from any repository and must be installed from source code. This section is heavily based on the instructions found at http://robertbasic.com/blog/install-pyqt5-in-python-3-virtual-environment/.

#### SIP

```
cd /tmp
wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.5/sip-4.16.5.tar.gz
tar xvfz sip-4.16.5.tar.gz
cd sip-4.16.5
python3.4 configure.py
make
sudo make install
```

#### PyQt5

Building PyQt5 from source will take a while.

```
cd /tmp
wget http://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.4/PyQt-gpl-5.4.tar.gz
tar xzf PyQt-gpl-5.4.tar.gz
cd PyQt-gpl-5.4
python3.4 configure.py --qmake /usr/bin/qmake-qt5
make
sudo make install
```

### Dynamips

Dynamips is a Cisco router emulator. It started as a separate project in 2005 but the sources are now part of the GNS3 repositories on Github.

```
cd /tmp
git clone https://github.com/GNS3/dynamips.git
cd dynamips/
mkdir build
cd build/
cmake .. -DDYNAMIPS_CODE=stable
make
sudo make install
```

### VPCS

The Virtual PC Simulator (VPCS) can be used in GNS3 to add simple PCs to a network topology. The steps below will install the /usr/local/bin/vpcs from source code.

```
cd /tmp
svn checkout http://svn.code.sf.net/p/vpcs/code/trunk vpcs
cd vpcs/src
./mk.sh 64
sudo install -m 755 vpcs /usr/local/bin
```

That's all.
