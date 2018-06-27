echo "Some GET examples:"
echo
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

echo "Thank you!"
