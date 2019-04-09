# Coffre-Fort

## Docker

### Build
    
    docker-compose build

### Deploy
    
    docker-compose up

## Local

### Requirements

    sh install.sh

or

    pip3 install -r TokenDealer/requirements.txt
    pip3 install -r ApiArp/requirements.txt
    pip3 install -r ApiUser/requirements.txt
    pip3 install -r FrontEnd/requirements.txt

#### Mongodb

##### Mac OS

install
    
    brew tap mongodb/brew  

start

    sudo brew services start mongodb-community@4.0

stop

    sudo brew services stop mongodb-community@4.0

##### Linux
##### Windows

#### Deployement

    python3 /ApiArp/src/arp.py &
    python3 /ApiUser/src/user.py 127.0.0.1 localhost &
    python3 /FrontEnd/src/frontend.py 127.0.0.1 127.0.0.1 &
    python3 /TokenDealer/src/tokenDealer.py 127.0.0.1 127.0.0.1
