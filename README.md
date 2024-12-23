# Clyde Ryde


## Table of Contents
- [Project Description](#project-description)
- [Project Artifacts](#project-artifacts)
- [Installation and Setup (Docker)](#installation-and-setup-docker)
    - [Prerequisites](#0-prerequisites)
    - [1. Clone the Project](#1-clone-the-project)
    - [2. Build and Run the Containers](#2-build-and-run-the-containers)
    - [3. [Optional] Run Commands in the Web Container](#3-optional-run-commands-in-the-web-container)
- [Usage](#usage)
    - [Sample User Data](#sample-user-data)
- [Development Setup (Without Docker)](#development-setup-without-docker)
    - [Prerequisites](#0-prerequisites-1)
    - [1. Clone the Project](#1-clone-the-project-1)
    - [2. Create a Python Virtual Environment](#2-create-a-python-virtual-environment)
    - [3. Install Project Requirements](#3-install-project-requirements)
    - [4. Create the Database & User](#4-create-the-database--user)
    - [5. Install Pre-Commit Hooks](#5-install-pre-commit-hooks)
    - [6. Run the Development Server](#6-run-the-development-server)
- [Management Commands to Add Dummy Data](#management-commands-to-add-dummy-data)
    - [Add Users](#add-users)
    - [Add Locations](#add-locations)
    - [Add Vehicles](#add-vehicles)
    - [Add Trips & Payments](#add-trips--payments)
- [Team Members](#team-members)

---

## Project Description
Clyde Ryde is an e-vehicle sharing platform that enables users to locate, rent, and return electric vehicles across various locations. The system is designed for customers to reserve vehicles, operators to manage and maintain the fleet, and managers to access usage reports. Built with **Django**, **PostgreSQL**, and **Redis**, Clyde Ryde provides a seamless experience for all users.


## Project Artifacts

* [Project Specification](/artifacts/project-spec-2024.pdf)
* [Project Report](/artifacts/Project-Report.pdf)
* [Video Report](/artifacts/LB03-04-Clyde-Ryde-Video-Report.mp4)
* [Feedback](/artifacts/LB03-04.pdf)


## Installation and Setup (Docker)

### 0. Prerequisites
Ensure [Docker Engine](https://docs.docker.com/engine/install/) and Docker Compose are installed:
```bash
docker --version
docker-compose --version
```

### 1. Clone the Project
```bash
git clone https://stgit.dcs.gla.ac.uk/programming-and-systems-development-m/2024/lb03-04/clyde-ryde.git
cd clyde-ryde
```

### 2. Build Image and Run the Containers
```bash
docker-compose up --build
```

### 3. [Optional] Run Commands in the Web Container
```bash
docker-compose exec web python manage.py showmigrations
```


## Usage
Users can view available vehicles, rent, and return them at selected locations. Operators manage the vehicle statuses (charging, repairing, etc.), while managers can view different reports on the usage.
This repository includes commands to set up and populate the application with sample data, which can be useful for testing and demonstration. This is done automatically if installed using Docker, or can be run manually (see: [Management Commands to Add Dummy Data](#management-commands-to-add-dummy-data)).

### Sample User Data
| Username | User Type | Password |
| :-------: | :------: | :------: |
| superuser | admin    | password |
| john      | customer | password |
| jane      | customer | password |
| emily     | customer | password |
| michael   | operator | password |
| william   | manager  | password |


## Development Setup (Without Docker)

### 0. Prerequisites

1. Install [Python 3.12](https://www.python.org/downloads/release/python-3120/)
    Verify the installation:
    ```bash
    python3.12 --version
    ```

2. Install [PostgreSQL 14](https://www.postgresql.org/download/)
    Verify the installation:
    ```bash
    psql --version
    ```

3. [Optional] Install [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/)
    Verify the installation:
    ```bash
    redis-server --version
    ```

### 1. Clone the Project
```bash
git clone https://stgit.dcs.gla.ac.uk/programming-and-systems-development-m/2024/lb03-04/clyde-ryde.git
cd clyde-ryde
```

### 2. Create a Python Virtual Environment
```bash
python3.12 -m venv venv/
source venv/bin/activate  # For MacOS/Linux
venv\Scripts\activate  # For Windows
```

### 3. Install Project Requirements
```bash
pip install -r requirements.txt
```

### 4. [Optional] Create the Database & User
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

### 5. Install Pre-Commit Hooks
```bash
pre-commit install
```

### 6. Run the Development Server
```bash
python manage.py runserver
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


# Team Members
1. Bairui Zhou ([2967515z@student.gla.ac.uk](mailto:2967515z@student.gla.ac.uk))
2. Chaoyue Wang ([2982958w@student.gla.ac.uk](mailto:2982958w@student.gla.ac.uk))
3. Siddhartha Pratim Dutta ([2897074d@student.gla.ac.uk](mailto:2897074d@student.gla.ac.uk))
4. Siwei Chen ([2970653c@student.gla.ac.uk](mailto:2970653c@student.gla.ac.uk))
5. Tingyu Zhou ([2691899z@student.gla.ac.uk](mailto:2691899z@student.gla.ac.uk))
6. Zhiqi Gao ([2995140g@student.gla.ac.uk](mailto:2995140g@student.gla.ac.uk))
7. Zhiying He ([2995174h@student.gla.ac.uk](mailto:2995174h@student.gla.ac.uk))

We hope you enjoy using Clyde Ryde!
