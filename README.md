# TRUSTSPACE API

## Quick start

To run project locally you can just type `docker-compose up`

## How to run the application

Conda is used for dedendency management.

if you want to manage python environment yourself with conda for example, the workflow is as follows:

* Create a conda env
* Activate conda env before performing any actions

You need to install all dependencies with conda

```bash
conda env update -f conda-env.yaml

# For developpers only
conda env update -f conda-env-dev.yaml
```

All parameters required are defined in `src/settings.py`, you can pass this parameters to the program using `dotenv run` program and `.env` file, or set  `EnvironmentFile` in your systemd-module.

### Applying migrations and startup

Before running the application don't forget to apply pending migrations.
You can apply migrations manualy:

```bash
# Migration
[dotenv run] alembic upgrade head
```

Or by setting environment variale `DB_MIGRATE` to true.

You can run the program in diffrent ways:

```bash
# dotenv + .env + python (Recommended)
dotenv run python src/server.py

# .env + docker-compose (Recommended)
docker-compose up

# predefined environment variables + python
python src/server.py

# predefined environment variables + custom server
hypercorn --bind localhost:8000 src/app:app
```
