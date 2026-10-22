import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def test_the_service_refuses_to_start_without_a_database_url(tmp_path):
    environment = {k: v for k, v in os.environ.items() if k != "DATABASE_URL"}

    # Start the real server from an empty folder, so there is no .env file either.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--app-dir",
            str(REPO),
            "--port",
            "0",
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,  # a failing exit is what this test expects
    )

    assert result.returncode != 0
    assert "database_url" in result.stderr
    assert "Field required" in result.stderr
