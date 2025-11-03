from pydantic import BaseModel, Field, conlist
from typing import List, Optional


class JobPosting(BaseModel):
    id: str
    title: str
    company: str
    country: str = Field(min_length=2, max_length=2)
    employment_type: Optional[str] = Field(default=None)
    tags: Optional[List[str]] = None


class RecommendationRequest(BaseModel):
    user_id: str
    context_tags: conlist(str, min_items=0) = []


class RecommendationResponse(BaseModel):
    user_id: str
    recommended_job_ids: conlist(str, min_items=0)

