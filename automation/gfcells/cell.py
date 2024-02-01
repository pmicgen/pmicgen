from dataclasses import dataclass

@dataclass
class Cell:
    name: str
    i: int
    j: int

    @property
    def z(self):
        return 0

    def __str__(self) -> str:
        return self.name