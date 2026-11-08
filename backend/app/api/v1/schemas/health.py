from pydantic import BaseModel


class LivenessOut(BaseModel):
    status: str
    app: str
    environment: str


class DatabaseHealthOut(BaseModel):
    status: str
    database: str