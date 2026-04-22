from pydantic import BaseModel
from typing import Literal


class GenerateRequest(BaseModel):
    activity_type: Literal["auto", "H5P.QuestionSet", "H5P.CoursePresentation"] = "auto"
    pass_percentage: int = 50


class GenerateResponse(BaseModel):
    filename: str
    content_type: str
    title: str
    download_path: str
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
