#!/bin/bash

if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo ".env file not found! Check if you are in the root directory."
  exit 1
fi

if [ -z "$DATABASE_NAME" ] || [ -z "$DATABASE_HOST" ] || [ -z "$DATABASE_PORT" ] || [ -z "$$DATABASE_USER" ] || [ -z "$DATABASE_PASSWORD" ]; then
  echo "Required database environment variables not set in .env file"
  exit 1
fi

echo "Setting up database: $DATABASE_NAME"

psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -d postgres -c "CREATE DATABASE \"$DATABASE_NAME\";"

psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -d postgres -c "CREATE ROLE \"$DATABASE_USER\" WITH LOGIN PASSWORD '$DATABASE_PASSWORD';"

psql -h "$DATABASE_HOST" -p "$DATABASE_PORT" -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE \"$DATABASE_NAME\" TO \"$DATABASE_USER\";"

echo "Database setup complete"
