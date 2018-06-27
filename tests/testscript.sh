#!/bin/bash

echo "Here are some curl-based example tests. Enjoy! :-)"
echo "Inserting first 8 complaints via POST. Press any key to proceed:"
read -n 1 -s

COUNTER=1
while [  $COUNTER -lt 9 ]; do
    echo "Inserting complaint # $COUNTER"
    curl -d "@entry$COUNTER.txt" -X POST http://localhost/complain
    let COUNTER=COUNTER+1
done

echo "First 8 entries were POSTed. Press any key to proceed: "
read -n 1 -s

echo "Modifying complaint #5's 'company' attribute via PATCH. Press any key to proceed:"
read -n 1 -s
curl -d 'complain={"company":"Sala%20da%20Justiça"}' -X PATCH http://localhost/complain/5
echo "Entry #5 was PATCHed. Press any key to proceed: "
read -n 1 -s

echo "Inserting 2 more complaints via POST. Press any key to proceed:"
read -n 1 -s
curl -d "@entry9.txt" -X POST http://localhost/complain
curl -d "@entry10.txt" -X POST http://localhost/complain
echo "Entries #9 and #10 were POSTed. Press any key to proceed: "
read -n 1 -s

echo "Updating complaint #9 via PUT. Press any key to proceed:"
read -n 1 -s
curl -d "@entry9_1.txt" -X PUT http://localhost/complain/9
echo "Entry #9 was modified via PUT. Press any key to proceed: "
read -n 1 -s

echo "Some GET examples: "
echo "Retrieving complaint #5: "
curl http://localhost/complain/5
echo "Press any key to proceed: "
read -n 1 -s

echo "Retrieving complaints made in a city which contains 'Paulo' in its name (case insensitive): "
curl http://localhost/complain?city_like=Paulo
echo "Press any key to proceed: "
read -n 1 -s

echo "Retrieving complaints made within a 3km-range from complaint #5: "
curl "http://localhost/complain?id=5&within_radius=3000"
echo "Press any key to proceed: "
read -n 1 -s

echo "Deleting complaint #9"
curl -X DELETE http://localhost/complain/9
echo "Press any key to proceed: "
read -n 1 -s

echo
echo "Thank you!"
