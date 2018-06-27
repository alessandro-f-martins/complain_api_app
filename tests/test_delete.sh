#!/bin/bash 

# COUNTER=1
# while [  $COUNTER -lt 11 ]; do
#     echo The counter is $COUNTER
#     cat "entry$COUNTER.txt"
#     let COUNTER=COUNTER+1
#     read -n 1 -s 
# done

COUNTER=1
while [  $COUNTER -lt 11 ]; do
    echo The counter is $COUNTER
    curl -X DELETE http://localhost/complain/$COUNTER
    let COUNTER=COUNTER+1
done


