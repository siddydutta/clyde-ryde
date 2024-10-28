# Clyde Ryde


## Description
TODO


## Usage
TODO


## Pre-Requisites
### 0. Install [Python 3.12](https://www.python.org/downloads/release/python-3120/)
Verify the installation:
```bash
python3.12 --version
```
**Python 3.12.x**

### 1. Install [PostgreSQL 14](https://www.postgresql.org/download/)
Verify the installation:
```bash
psql --version
```
**psql (PostgreSQL) 14.xx**

### 2. [Optional] Install [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
Verify the installation:
```bash
redis-server --version
```
**Redis server v=7.x.x**

## Development

### 0. Clone the Project
```bash
git clone https://stgit.dcs.gla.ac.uk/programming-and-systems-development-m/2024/lb03-04/clyde-ryde.git
cd clyde-ryde
```

### 1. Create a Python Virtual Environment
```bash
python3.12 -m venv venv/
```
For MacOS/Linux:
```bash
source venv/bin/activate
```
For Windows:
```bash
venv\Scripts\activate
```

### 2. Install Project Requirements
```bash
pip install -r requirements.txt
```

### 3. Create the Database & User
```bash
chmod +x scripts/init_db.sh
./scripts/init_db.sh
```
**OR** run the following SQL statements:
```sql
CREATE DATABASE "clyde_ryde";
CREATE ROLE "admin" WITH LOGIN PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE "clyde_ryde" TO "admin";
```

### 4. Install Pre-Commit Hooks
```bash
pre-commit install
```

### 5. Run the Development Server
```bash
python manage.py runserver
```


## [Optional] Docker Support

### 0. Install [Docker Engine](https://docs.docker.com/engine/install/)
Verify the installation:
```bash
docker --version
docker-compose --version
```

### 1. Build and Run the Containers
```bash
docker-compose up --build
```

### 2. Running Commands in the Web Container
```bash
docker-compose exec web python manage.py createsuperuser
```


## Management Commands to Add Dummy Data
### Add Users
```shell
python manage.py add_users
```
> Password for all users is _password_.

### Add Locations
```shell
python manage.py add_locations
```

### Add Vehicles
```shell
python manage.py add_vehicles --number 15
```

### Add Trips & Payments
```shell
python manage.py add_trips --start_date 2024-10-01 --number 30
```
