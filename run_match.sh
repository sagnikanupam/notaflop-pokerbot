#!/usr/bin/env bash

for i in {1..10}
do
    python3 engine.py
    grep "Final" ./gamelog.txt
done