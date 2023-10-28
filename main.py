import argparse
import os
import subprocess

from hypercorn.config import Config
from hypercorn.run import run

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Help command for Oniverse API")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-e", "--dotenv", action="store_true", help="Load .env file")
    parser.add_argument("-m", "--migrate", action="store_true", help="Run database migrations")
    parser.add_argument("-i", "--init", action="store_true", help="Initialize database")
    parser.add_argument("-r", "--reload", action="store_true", help="Start in reload mode", default=False)
    args, unknown = parser.parse_known_args()

    if unknown:
        parser.print_help()
        exit(1)

    if args.dotenv:
        from dotenv import load_dotenv

        load_dotenv()

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))
    log_level = os.environ.get("LOG_LEVEL", "info").upper()
    workers = int(os.environ.get("WORKERS", "1"))
    root_path = os.environ.get("ROOT_PATH", "")
    db_migrate = os.environ.get("DB_MIGRATE", "false")
    db_init = os.environ.get("DB_INIT", "false")

    if db_migrate == "true" or args.migrate:
        subprocess.run(["alembic", "upgrade", "heads"])

    if db_init == "true" or args.init:
        subprocess.run(["python", "src/initdb.py"])

    config = Config()
    config.application_path = "src/app.py"
    config.bind = [f"{host}:{port}"]
    config.loglevel = log_level
    config.accesslog = "-"
    config.workers = workers
    config.root_path = root_path
    config.use_reloader = args.reload

    run(config)
