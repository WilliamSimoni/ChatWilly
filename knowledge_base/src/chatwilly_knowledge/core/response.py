from typing import List

from pydantic import BaseModel, Field


class CategoryChunk(BaseModel):
    """Represents a single atomic piece of information extracted from the text."""

    text: str = Field(
        ...,
        description="The narrative paragraph, in first person, containing the complete anecdote.",
    )
    category: str = Field(
        ..., description="The specific category this information belongs to."
    )
    keywords: List[str] = Field(
        ...,
        description="A list of 3-5 lowercase keywords relevant to this chunk for search.",
    )


class ExtractionResponse(BaseModel):
    """The container for the list of chunks."""

    chunks: List[CategoryChunk] = Field(
        ...,
        description="The list of extracted chunks, in strict chronological order as they appear in the text.",
    )
