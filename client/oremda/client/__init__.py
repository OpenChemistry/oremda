from importlib import resources
from pathlib import Path
from fastapi.staticfiles import StaticFiles

with resources.path("oremda.client", "__init__.py") as path:
    client_package_path = path.parent

client_build = StaticFiles(
    directory=Path(str(client_package_path)) / "build", html=True
)
