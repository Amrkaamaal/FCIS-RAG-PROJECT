from pydantic import BaseModel, Field


class PushDataRequest(BaseModel):

  do_reset: bool = False


class SearchRequest(BaseModel):

  text: str = Field(..., min_length=1)

  top_k: int = Field(5, ge=1, le=50)
