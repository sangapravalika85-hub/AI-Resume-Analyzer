from pydantic import BaseModel, Field

class JobMatchRequest(BaseModel):
    title: str = Field(default="Job description", max_length=180)
    description: str = Field(min_length=10)
    resume_ids: list[int] | None = None
