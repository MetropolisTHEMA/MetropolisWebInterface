# MetroWeb: Web Interface for Metropolis

MetroWeb is a Django site, used as a web interface for the Metropolis simulator.

## Installation

### Manual Installation

1. Install prerequisites: `Python3`, `PostgreSQL` and `PostGIS`.
2. Clone the repository with `git clone https://github.com/aba2s/Metropolis && cd Metropolis`.
3. Setup a Python virtual environment with `virtualenv -p /usr/bin/python3 venv`.
4. Activate the virtual environment with `source ./venv/bin/activate`.
5. Install required Python packages with `pip install -r requirements.txt`.
6. Create a PostgreSQL user and database.
7. Create a `settings.json` file in the current directory with the following content:
```json
{
    "debug": true,
    "secret_key": "YOUR_SECRET_KEY",
    "database": {
        "name": "DB_NAME",
        "user": "DB_USER",
        "password": "DB_PASSWORD"
    }
}
```
8. Migrate the database with `python3 manage.py makemigrations metro_app` and `python3 manage.py migrate`.
9. Run the server with `python3 manage.py runserver`.
