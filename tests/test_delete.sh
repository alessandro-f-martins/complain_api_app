#!/bin/bash 

echo "Deleting complaints ids #1 to #10"
read -n 1 -s
COUNTER=1
while [  $COUNTER -lt 11 ]; do
    echo The counter is $COUNTER
    curl -X DELETE http://localhost/complain/$COUNTER
    let COUNTER=COUNTER+1
done


