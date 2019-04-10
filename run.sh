#!/bin/bash

exec python3 /ApiArp/src/arp.py &
exec python3 /ApiUser/src/user.py 127.0.0.1 localhost &
exec python3 /FrontEnd/src/frontend.py 127.0.0.1 127.0.0.1 &
exec python3 /TokenDealer/src/tokenDealer.py 127.0.0.1 127.0.0.1
