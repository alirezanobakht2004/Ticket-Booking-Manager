#!/bin/bash

DB_USER="root"
DB_PASS="" 

SQL_FOLDER="create_tables/"


if [ ! -d "$SQL_FOLDER" ]; then
    echo "SQL folder $SQL_FOLDER does not exist."
    exit 1
fi


for sql_file in $(ls "$SQL_FOLDER"/*.sql | sort); do
    echo "Executing $sql_file..."
    mysql -u"$DB_USER" -p"$DB_PASS" < "$sql_file"
done

echo "All SQL files executed successfully."
