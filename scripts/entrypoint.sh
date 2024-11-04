#!/bin/bash

set -e

# Run migrations
python manage.py migrate

# Attempt to populate DB
python manage.py add_users
python manage.py add_locations
python manage.py add_vehicles --number 15
python manage.py add_trips --start_date 2024-10-01 --number 50

# Start server
python manage.py runserver 0.0.0.0:8000
