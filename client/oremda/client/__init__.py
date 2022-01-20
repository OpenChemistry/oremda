from importlib import resources
from pathlib import Path
from fastapi.staticfiles import StaticFiles

client_package_path = resources.files("oremda.client")

client_build = StaticFiles(
    directory=Path(str(client_package_path)) / "build", html=True
)
