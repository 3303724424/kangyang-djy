import json
from pathlib import Path


class LocalRepository:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or Path(__file__).resolve().parents[2] / "data"

    def load(self, name: str) -> list[dict]:
        path = self.data_dir / f"{name}.json"
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @property
    def attractions(self) -> list[dict]:
        return self.load("attractions")

    @property
    def hotels(self) -> list[dict]:
        return self.load("hotels")

    @property
    def companions(self) -> list[dict]:
        return self.load("companions")
