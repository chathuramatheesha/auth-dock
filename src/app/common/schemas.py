from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(frozen=True)
class MessageOutDTO:
    message: str


class MessageOut(BaseModel):
    message: str
