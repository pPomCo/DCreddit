# DCreddit


## Team

 - J. DOUCET 
 - J. HUTEAU
 - J. LOVON
 - P. POMERET-COQUOT

## Documents

 - [Document de suivi](doc/suivi.md) 


## Installation

### Install PyLucene

    # Download PyLucene 8.1.1 at https://lucene.apache.org/pylucene/install.html
    # Enter directory and follow given install instructions
    
    # Step-by-step
    
    # 1. Install Ant (if needed)
    sudo apt-get install ant
    
    # 2. Install JCC (inside lucene downloaded directory)
    cd jcc/
    # Edit setup.py to match your environment (check JDK path)
    python3 setup.py build
    sudo python3 setup.py install
    cd ../

    # 3. Install PyLucene
    # Edit Makefile to match your environment (uncomment lines, check JDK path)
    make
    make test # look for failures
    sudo make install
    