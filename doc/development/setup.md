# PyQt5 setup 

## Ubuntu

In order to run a PyQt5 application, you need to install the package `python-pyqt5`:
```bash
$ sudo apt-get install python-pyqt5
```

(tested with Ubuntu 16.04 and 18.04)

### Qt Libraries and Python Bindings

The following packages and install steps are needed if qt5 c++ development libraries have not yet been installed. Generally, it is recommended to install the `qt5-default` package and C++ development libraries.

        $ sudo apt-get install qttools5-dev-tools
        $ sudo apt-get install qttools5.dev  


Step 2: **To get the plugin loader** (have to build PyQt from source)
        
        Select Versions
       
         $ export QT_SELECT=qt5
         $ qmake --version
         $ QMake version 3.1
         $ Using Qt version 5.9.5 in /usr/lib/x86_64-linux-gnu  


Step 3: **Build SIP**

        $ wget https://sourceforge.net/projects/pyqt/files/sip/sip-4.19.8/sip-4.19.8.tar.gz
        $ tar xzvf sip-4.19.8.tar.gz
        $ cd sip-4.19.8
        $ python configure.py
        $ make
        $ sudo make install  


Step 4: **Build PyQt5**

        $ wget https://sourceforge.net/projects/pyqt/files/PyQt5/PyQt-5.10.1/PyQt5_gpl-5.10.1.tar.gz
        $ tar xzvf PyQt5_gpl-5.10.1.tar.gz
        $ cd PyQt5_gpl-5.10.1
        $ python configure.py
        $ make
        $ sudo make install

