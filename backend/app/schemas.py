"""Public API contracts, separate from storage and inference."""
from pydantic import BaseModel, Field, field_validator


class SessionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name", mode="before")
    @classmethod
    def normalise_name(cls, value):
        # The student supplies the topic; it is not guessed from a document.
        return " ".join(value.split()) if isinstance(value, str) else value


class StudySession(BaseModel):
    id: str
    name: str
    created_at: str
    updated_at: str
