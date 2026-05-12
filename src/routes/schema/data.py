from pydantic import BaseModel, Field, model_validator


class RequestProcess(BaseModel):

  chunk_size: int = Field(500, ge=1)

  overlap: int = Field(50, ge=0)

  do_reset: bool = False

  @model_validator(mode="after")
  def validate_overlap(self):

    if self.overlap >= self.chunk_size:

      raise ValueError("overlap must be smaller than chunk_size")

    return self
