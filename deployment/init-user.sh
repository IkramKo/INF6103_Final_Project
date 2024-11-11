#!/bin/bash

# PostgreSQL credentials
PGHOST="localhost"  # Change if needed, for Docker setup use the name of the service (e.g. postgres)
PGUSER="myuser"
PGPASSWORD="mypassword"
PGDATABASE="mydb"

# Docker compose service name for Mosquitto
MOSQUITTO_SERVICE="mosquitto"

# SQL query to fetch sensor_name and psswd
SQL_QUERY="SELECT sensor_name AS name, psswd FROM INF6103.Sensor UNION ALL SELECT actuator_name as name, psswd FROM INF6103.Actuator;"

# Get the list of sensor_name and password pairs from PostgreSQL
sensor_data=$(PGPASSWORD=$PGPASSWORD psql -h "$PGHOST" -U "$PGUSER" -d "$PGDATABASE" -t -A -F"," -c "$SQL_QUERY")

# Loop through the sensor data and add each to Mosquitto's password file
echo "Adding users to Mosquitto..."
echo $sensor_data

# Loop through each line from the query result
# Store the pairs in an array
pairs=()

# Split the input string by spaces
for pair_str in $sensor_data; do
    # Split each pair by comma
    IFS=',' read usr passwd <<< "$pair_str"

    # Store the pair in the array (using associative array for better clarity)
    declare -A pair
    pair["usr"]="$usr"
    pair["passwd"]="$passwd"
    pairs+=("(${pair[usr]},${pair[passwd]})")  # Store as a tuple string
done

# Fix the permissions of the Mosquitto password file to make it secure
echo "Fixing permissions on the Mosquitto password file..."
sudo docker compose exec "$MOSQUITTO_SERVICE" chown root:root /mosquitto/config/pwfile
sudo docker compose exec "$MOSQUITTO_SERVICE" chmod 600 /mosquitto/config/pwfile

echo "Printing everything"
for pair_str in "${pairs[@]}"; do
    # Extract usr and passwd from the tuple string
    IFS=',' read usr passwd <<< "${pair_str//[( )]}" # Remove parentheses
    echo "usr:$usr, passwd:$passwd"
    sudo docker compose exec -T "$MOSQUITTO_SERVICE" mosquitto_passwd -b /mosquitto/config/pwfile "$usr" "$passwd"
done

# Adding the PLC user
sudo docker compose exec -T "$MOSQUITTO_SERVICE" mosquitto_passwd -b /mosquitto/config/pwfile "plc_usr" "plc_passwd"

# Optionally restart Mosquitto to ensure the changes take effect
echo "Restarting Mosquitto broker..."
sudo docker compose restart "$MOSQUITTO_SERVICE"

echo "Done!"