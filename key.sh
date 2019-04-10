#!/usr/bin/env bash

exec openssl genrsa 1024 > TokenDealer/src/key.txt
exec openssl genrsa 1024 > FrontEnd/src/key.txt
