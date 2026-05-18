from pydantic import BaseModel


class AnalyzedSchema(BaseModel):
    destructive: bool
    reason: str