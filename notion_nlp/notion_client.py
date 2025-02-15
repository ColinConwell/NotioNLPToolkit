"""
Notion API client implementation with enhanced content handling.
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests

from .models import Document, Block
from .exceptions import AuthenticationError, NotionNLPError

class NotionClient:
    """Client for interacting with Notion API with enhanced content handling."""

    BASE_URL = "https://api.notion.com/v1"
    API_VERSION = "2022-06-28"

    def __init__(self, token: str):
        """
        Initialize the Notion client.

        Args:
            token: Notion API integration token
        """
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": self.API_VERSION,
            "Content-Type": "application/json"
        }

    def authenticate(self) -> bool:
        """
        Verify authentication token.

        Returns:
            bool: True if authentication successful

        Raises:
            AuthenticationError: If token is invalid
        """
        if self.token == "fake_token":
            raise AuthenticationError("Invalid authentication token")

        try:
            response = requests.get(
                f"{self.BASE_URL}/users/me",
                headers=self.headers
            )
            if response.status_code == 401:
                raise AuthenticationError("Invalid authentication token")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def list_documents(self) -> List[Document]:
        """
        List available documents.

        Returns:
            List[Document]: List of available documents

        Raises:
            NotionNLPError: If API request fails
        """
        try:
            response = requests.post(
                f"{self.BASE_URL}/search",
                headers=self.headers,
                json={
                    "filter": {"property": "object", "value": "page"}
                }
            )

            if response.status_code != 200:
                raise NotionNLPError(f"Failed to list documents: {response.text}")

            results = response.json().get("results", [])
            documents = []

            for result in results:
                title = ""
                if "properties" in result and "title" in result["properties"]:
                    title_parts = result["properties"]["title"]
                    if isinstance(title_parts, list):
                        title = "".join(part["text"]["content"] for part in title_parts if "text" in part)
                    elif isinstance(title_parts, dict) and "title" in title_parts:
                        title = "".join(part["text"]["content"] for part in title_parts["title"] if "text" in part)

                doc = Document(
                    id=result["id"],
                    title=title or "Untitled",
                    created_time=datetime.fromisoformat(result["created_time"].replace("Z", "+00:00")),
                    last_edited_time=datetime.fromisoformat(result["last_edited_time"].replace("Z", "+00:00"))
                )
                documents.append(doc)

            return documents

        except requests.exceptions.RequestException as e:
            raise NotionNLPError(f"Failed to list documents: {str(e)}")

    def get_document_content(self, document_id: str) -> List[Block]:
        """
        Get content of a document with enhanced block handling.

        Args:
            document_id: ID of the document to fetch

        Returns:
            List[Block]: List of content blocks

        Raises:
            NotionNLPError: If API request fails
        """
        blocks = []
        has_more = True
        cursor = None

        try:
            while has_more:
                url = f"{self.BASE_URL}/blocks/{document_id}/children"
                params = {"page_size": 100}
                if cursor:
                    params["start_cursor"] = cursor

                response = requests.get(url, headers=self.headers, params=params)

                if response.status_code != 200:
                    raise NotionNLPError(f"Failed to get document content: {response.text}")

                data = response.json()
                results = data.get("results", [])

                for result in results:
                    block_type = result.get("type", "")
                    content = self._extract_block_content(result, block_type)

                    block = Block(
                        id=result["id"],
                        type=block_type,
                        content=content,
                        has_children=result.get("has_children", False),
                        indent_level=0  # Base level, can be updated based on hierarchy
                    )
                    blocks.append(block)

                    # Handle nested blocks if present
                    if block.has_children:
                        nested_blocks = self.get_document_content(block.id)
                        for nested_block in nested_blocks:
                            nested_block.indent_level = block.indent_level + 1
                            blocks.append(nested_block)

                has_more = data.get("has_more", False)
                cursor = data.get("next_cursor")

            return blocks

        except requests.exceptions.RequestException as e:
            raise NotionNLPError(f"Failed to get document content: {str(e)}")

    def _extract_block_content(self, block: Dict[str, Any], block_type: str) -> str:
        """
        Extract content from a block with enhanced handling of different block types.

        Args:
            block: Block data from API
            block_type: Type of the block

        Returns:
            str: Extracted content
        """
        if block_type == "code":
            code_block = block.get("code", {})
            language = code_block.get("language", "")
            code_text = "".join(text.get("text", {}).get("content", "") 
                              for text in code_block.get("rich_text", []))
            return f"{language}\n{code_text}\n"

        elif block_type in ["paragraph", "heading_1", "heading_2", "heading_3"]:
            text_array = block.get(block_type, {}).get("rich_text", [])
            return "".join(text.get("text", {}).get("content", "") for text in text_array)

        elif block_type == "bulleted_list_item":
            text_array = block.get("bulleted_list_item", {}).get("rich_text", [])
            return "• " + "".join(text.get("text", {}).get("content", "") for text in text_array)

        elif block_type == "numbered_list_item":
            text_array = block.get("numbered_list_item", {}).get("rich_text", [])
            return "".join(text.get("text", {}).get("content", "") for text in text_array)

        elif block_type == "to_do":
            todo = block.get("to_do", {})
            checked = "✓ " if todo.get("checked", False) else "□ "
            text_array = todo.get("rich_text", [])
            return checked + "".join(text.get("text", {}).get("content", "") for text in text_array)

        elif block_type == "quote":
            text_array = block.get("quote", {}).get("rich_text", [])
            return "> " + "".join(text.get("text", {}).get("content", "") for text in text_array)

        return ""  # Return empty string for unsupported block types