"""
Data models for the Notion NLP library.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class Document(BaseModel):
    """Represent a Notion document."""
    id: str
    title: str
    created_time: datetime
    last_edited_time: datetime

class Block(BaseModel):
    """Represent a block of content in a Notion document."""
    id: str
    type: str
    content: str
    has_children: bool = False

class Tag(BaseModel):
    """Represent a tag applied to content."""
    name: str
    type: str
    category: str