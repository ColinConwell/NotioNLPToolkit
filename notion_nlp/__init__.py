"""
Notion NLP Library - Process Notion documents with NLP capabilities and hierarchical organization.
"""

from .notion_client import NotionClient
from .text_processor import TextProcessor
from .hierarchy import DocumentHierarchy
from .tags import Tagger
from .models import Document, Block, Tag
from .exceptions import NotionNLPError, AuthenticationError

__version__ = "0.1.0"
__all__ = [
    "NotionClient",
    "TextProcessor",
    "DocumentHierarchy",
    "Tagger",
    "Document",
    "Block",
    "Tag",
    "NotionNLPError",
    "AuthenticationError",
]
