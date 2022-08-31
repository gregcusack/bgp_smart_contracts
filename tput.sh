#!/bin/bash

for i in {0..200}
do
    python src/add_advertisement.py ACCOUNT0 10.0.20.0 24 2 & &> /dev/null
    python src/add_advertisement.py ACCOUNT1 10.0.20.0 24 3 & &> /dev/null
    python src/add_advertisement.py ACCOUNT2 10.0.20.0 24 4 & &> /dev/null
done

echo "finished running loop. waiting for completion..."
wait

echo 'done'

