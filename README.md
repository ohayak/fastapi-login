# TRUSTSPACE API

## Quick start

To run project locally you can just type `docker-compose up`. First time may fail, restart.

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

## Applying migrations and startup

Before running the application don't forget to apply pending migrations.
You can apply migrations manualy:

```bash
[dotenv run] alembic upgrade heads
```

Or automaticly, by setting environment variable `DB_MIGRATE=true`  or just apppend `--migrate` option to `./start.sh` command

All parameters required are defined in `src/settings.py`, you can pass this parameters to the program inside a `.env` file and start the server with `./start.sh --dotenv`.
You can also use `dotenv run <command>` to load parameters from `.env` file with any command.

How `.env` looks like:

```bash

# Configuration of auth database used for login (managed by alembic)
DB_AUTH_HOST=<ip, localhost etc>
DB_AUTH_PORT=5432
DB_AUTH_NAME=auth
DB_AUTH_USER=auth
DB_AUTH_PASSWORD="my-password"

# Configuration of scheduler database
DB_SCHEDULER_HOST=<ip, localhost etc>
DB_SCHEDULER_PORT=5432
DB_SCHEDULER_NAME=scheduler
DB_SCHEDULER_USER=scheduler
DB_SCHEDULER_PASSWORD="other password"

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
```

/!\ `.env` file contains sensible informations like database IP and passwords, never push this file to git repository.

## How to build images

The easiest way if to push a tag to git and Bitbucket Pipelines will create a new image and push it. If you want to do this step your self, just execute comands defined on the `bitbucket-pipelines.yaml` in your machine

## Bitbucket pipelines

Please refer to `bitbucket-pipelines.yaml` and Bitbucket pipelines documentation
/!\ Environment variables used in the pipeline, are defined via the web interface manually. Check [Repository varaibles](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)