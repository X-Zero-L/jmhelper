from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    jm_clear: bool = True
