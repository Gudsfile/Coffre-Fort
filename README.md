# Coffre-Fort



🖥 Service Oriented Architectures Project developed in March/April 2019.



⚙️ The following technologies were used to carry out this project:

* Python
* Flask
* Mongodb
* ZMQ
* JWT
* Docker



🔒 The project consists of protecting a resource by using four services :

* ApiUser (REST API, Database access)
* ApiArp (REST API, Protected Resource Access)
* TokenDealer
* FrontEnd



⚠️ Before deploying the application, it is **advisable to modify the key.txt** files of the Token Dealer and FrontEnd:

    sh key.sh

or 

    openssl genrsa 1024 > TokenDealer/src/key.txt
    openssl genrsa 1024 > FrontEnd/src/key.txt

## Docker

Deployment on Docker uses docker-composite. 
Four services are deployed on the same network.

##### Build

    docker-compose build

##### Deploy

    docker-compose up

## Local

#### Python requirements

    sh install.sh

or

    pip3 install -r TokenDealer/requirements.txt
    pip3 install -r ApiArp/requirements.txt
    pip3 install -r ApiUser/requirements.txt
    pip3 install -r FrontEnd/requirements.txt

#### Mongodb

###### Mac OS

install

    brew tap mongodb/brew  

start

    sudo brew services start mongodb-community@4.0

stop

    sudo brew services stop mongodb-community@4.0

###### Linux

###### Windows

#### Deployement

    python3 arp.py 127.0.0.1 &
    python3 user.py 127.0.0.1 localhost &
    python3 frontend.py 127.0.0.1 127.0.0.1 &
    python3 tokenDealer.py

#### Test

Sign

    curl -i 'http://localhost:5002/api/create' -d '{"LOGIN":"test", "PASSWORD":"test"}' -H 'Content-Type: application/json'

> HTTP/1.0 200 OK



Login

    curl -i 'http://127.0.0.1:5002/api/user/signin?LOGIN=test&PASSWORD=test'

> HTTP/1.0 200 OK
> Content-Type: application/json
> "{"LOGIN": "test", "PASSWORD": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJMT0dJTiI6InRlc3QiLCJQQVNTV09SRCI6InRlc3QifQ.rJLrX8aYJRZhUnkExmEyyRj6E56WWWsfz2IL1fLFBlw"}"

    curl -i 'http://127.0.0.1:5002/api/user/signin?LOGIN=test&PASSWORD=toto'

> HTTP/1.0 404 NOT FOUND
> Content-Type: application/json
> {
>   "Error": "Unknown"
> }



Access to the resource

    curl -i 'http://127.0.0.1:5001/api?LOGIN=test' -H 'Authorization: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJMT0dJTiI6InRlc3QiLCJQQVNTV09SRCI6InRlc3QifQ.rJLrX8aYJRZhUnkExmEyyRj6E56WWWsfz2IL1fLFBlw'

> HTTP/1.0 200 OK
> Content-Type: application/json
> {
>   "Authorization": "OK",
>   "Ressource": "the_secret"
> }

    curl -i 'http://127.0.0.1:5001/api?LOGIN=test' -H 'Authorization: wrong_token'

> HTTP/1.0 409 CONFLICT
> Content-Type: application/json
> {
>   "Authorization": "KO"
> }
