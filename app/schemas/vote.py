from typing import Literal
from pydantic import BaseModel


class VoteBase(BaseModel):
    post_id: int
    dir: Literal[0, 1] 