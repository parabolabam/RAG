# Define a Pydantic model
from pydantic import BaseModel


class Article(BaseModel):
    link: str
