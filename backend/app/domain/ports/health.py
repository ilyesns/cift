from typing import Protocol


class DatabaseProbe(Protocol):
    def ping(self) -> None:
        """Return normally if the database answers; raise any exception otherwise."""
        ...