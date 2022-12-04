import subprocess

from settings import settings

if __name__ == "__main__":
    cmd = [
        "hypercorn",
        "--bind",
        f"{settings.host}:{settings.port}",
        "--log-level",
        settings.log_level,
        "--workers",
        str(settings.workers),
    ]

    if settings.reload:
        cmd.append("--reload")

    if settings.accesslog:
        cmd.extend(["--access-logfile", "-"])
    
    if settings.errorlog:
        cmd.extend(["--error-logfile", "-"])

    if settings.root_path:
        cmd.extend(["--root-path", settings.root_path])

    cmd.append("src/app:app")

    print("Server running:")
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
