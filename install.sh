#!/bin/bash

exec pip3 install -r ApiArp/requirements.txt &
exec pip3 install -r ApiUser/requirements.txt &
exec pip3 install -r FrontEnd/requirements.txt &
exec pip3 install -r TokenDealer/requirements.txt