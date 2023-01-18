# BIB API

## Quick start

To run project locally you can just type `docker-compose up`. First time may fail, restart.

## Install depenedencies

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

## Settings

All parameters required are defined in `src/core/config.py`, you can pass this parameters to the program inside a `.env` file and start the server with `./start.sh --dotenv`.
You can also use `dotenv run <command>` to load parameters from `.env` file with any command.

How `.env` looks like:

```bash

# Configuration of auth database used for login (managed by alembic)
DB_AUTH_HOST=<ip, localhost etc>
DB_AUTH_PORT=5432
DB_AUTH_NAME=auth
DB_AUTH_USER=auth
DB_AUTH_PASSWORD="my-password"

# Configuration of batetry data database
DB_DATA_HOST=<ip, localhost etc>
DB_DATA_PORT=5432
DB_DATA_NAME=data
DB_DATA_USER=data
DB_DATA_PASSWORD="my-password"

# logs verbosity DEBUG > INFO > WARNING > ERROR
LOG_LEVEL=INFO

# hotreload: restart server each time you edit a file, usefile for developpers
RELOAD=true

# enable or not access logs
ACCESSLOG=true

# enable or not error logs
ERRORLOG=true

# run database migration before startup
DB_MIGRATE=true

# init database before startup
DB_INIT=true
```

/!\ `.env` file contains sensible informations like database IP and passwords, never push this file to git repository.

## Startup

Before running the application don't forget to apply pending migrations.
You can apply migrations manualy:

```bash
alembic upgrade heads
```

Or automaticly, by setting environment variables `DB_MIGRATE=true` and `DB_INIT=true`, or just apppend `--migrate` and `--init` options to `./start.sh` command

```bash
# use --dotenv to load .env file
# Examples
./start.sh --dotenv
./start.sh --init --migrate
./start
```

## Pushing data at startup

If you need to create new users/roles/groups use `src/initdb.py` script to push new entitites to database and run `./start.sh --init` to make the changes at startup.

## How to build images

The easiest way if to push a tag to git and Bitbucket Pipelines will create a new image and push it. If you want to do this step your self, just execute comands defined on the `bitbucket-pipelines.yaml` in your machine

## Bitbucket pipelines

Please refer to `bitbucket-pipelines.yaml` and Bitbucket pipelines documentation
/!\ Environment variables used in the pipeline, are defined via the web interface manually. Check [Repository varaibles](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)

## Database migration tools

Please check [Alembic](https://alembic.sqlalchemy.org/en/latest/) for details. Below a list of must used commands

```bash
# upgrade database to the latest version
alembic upgrade heads

# downgrade database
alembic downgrade heads-1

# generate empty migration
alembic revision -m "some comment"

# generate migration
alembic revision --autogenerate -m "some comment"
```
