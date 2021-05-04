# MetroWeb: Web Interface for Metropolis

MetroWeb is a Django site, used as a web interface for the Metropolis simulator.

## Installation

### Manual Installation

1. Install prerequisites: `Python3`, `PostgreSQL`, `PostGIS` and `Redis`.
2. Clone the repository with `git clone https://github.com/aba2s/Metropolis && cd Metropolis`.
3. Setup a Python virtual environment with `virtualenv -p /usr/bin/python3 venv`.
4. Activate the virtual environment with `source ./venv/bin/activate`.
5. Install required Python packages with `pip install -r requirements.txt`.
6. Create a PostgreSQL user and database.
7. Configure and start a Redis server.
8. Create a `settings.json` file in the current directory with the following content:
```json
{
    "debug": true,
    "secret_key": "YOUR_SECRET_KEY",
    "database": {
        "name": "DB_NAME",
        "user": "DB_USER",
        "password": "DB_PASSWORD"
    },
    "rq_queues": {
        "host": "REDIS_HOST",
        "port": "REDIS_PORT",
        "db_default": "REDIS_DB_ID",
        "db_simulations": "REDIS_DB_ID",
        "password": "REDIS_PASSWORD"
    }
}
```
9. Migrate the database with `python3 manage.py makemigrations metro_app` and `python3 manage.py migrate`.
10. Run the server with `python3 manage.py runserver`.
11. Run RQ workers with `python3 manage.py rqworker default simulations`.

### Building the Docs

MetroWeb's documentation is written with Sphinx.

To build the docs, change directory to `Metropolis/docs/` and run `make html`.

## Relevant Documentations

- [Django](https://docs.djangoproject.com/en/3.2/)
- [Sphinx](https://www.sphinx-doc.org/en/master/contents.html)
- [Folium](https://python-visualization.github.io/folium/)
- [Leaflet](https://leafletjs.com/reference-1.7.1.html)
- [Redis Queue](https://python-rq.org/docs/workers/)
- [django-rq](https://github.com/rq/django-rq)
