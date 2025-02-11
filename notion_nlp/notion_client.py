"""
Notion API client implementation.
"""
from typing import List, Dict, Optional
from datetime import datetime
import requests
from pydantic import BaseModel
from .models import Document, Block
from .exceptions import AuthenticationError, NotionNLPError

class NotionClient:
    """Handle interactions with the Notion API."""

    def __init__(self, auth_token: str):
        """
        Initialize the Notion client.

        Args:
            auth_token: Notion API authentication token
        """
        self.auth_token = auth_token
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def authenticate(self) -> bool:
        """
        Verify authentication credentials.

        Returns:
            bool: True if authentication is successful

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            response = requests.get(
                f"{self.base_url}/users/me",
                headers=self.headers
            )
            if response.status_code != 200:
                raise AuthenticationError(f"Authentication failed: {response.text}")
            return True
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def list_documents(self) -> List[Document]:
        """
        List all available documents.

        Returns:
            List[Document]: List of document objects

        Raises:
            NotionNLPError: If there's an error listing documents
        """
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={
                    "filter": {
                        "value": "page",
                        "property": "object"
                    },
                    "sort": {
                        "direction": "descending",
                        "timestamp": "last_edited_time"
                    }
                }
            )

            if response.status_code != 200:
                raise NotionNLPError(f"Failed to list documents: {response.text}")

            data = response.json()
            if not isinstance(data, dict) or 'results' not in data:
                raise NotionNLPError(f"Invalid response format: {data}")

            results = data.get("results", [])
            documents = []

            for page in results:
                try:
                    # Get page properties including title
                    title = self._extract_page_title(page)
                    etag = page.get("etag", None)

                    doc = Document(
                        id=page["id"],
                        title=title,
                        created_time=datetime.fromisoformat(page["created_time"].replace('Z', '+00:00')),
                        last_edited_time=datetime.fromisoformat(page["last_edited_time"].replace('Z', '+00:00')),
                        etag=etag
                    )
                    documents.append(doc)
                except Exception as e:
                    print(f"Warning: Failed to process page {page.get('id', 'unknown')}: {str(e)}")
                    continue

            return documents

        except Exception as e:
            raise NotionNLPError(f"Error listing documents: {str(e)}")

    def _extract_page_title(self, page: Dict) -> str:
        """Extract title from page properties."""
        title = "Untitled"
        try:
            properties = page.get("properties", {})

            # Look for title in different possible locations
            title_property = None
            if "title" in properties:
                title_property = properties["title"]
            elif "Name" in properties:
                title_property = properties["Name"]

            if isinstance(title_property, list) and title_property:
                title = title_property[0].get("text", {}).get("content", "Untitled")
            elif isinstance(title_property, dict):
                title_items = title_property.get("title", [])
                if title_items and isinstance(title_items, list):
                    title = title_items[0].get("text", {}).get("content", "Untitled")

        except Exception:
            pass

        return title

    def get_document_content(self, document_id: str) -> List[Block]:
        """
        Retrieve the content of a specific document.

        Args:
            document_id: The ID of the document to retrieve

        Returns:
            List[Block]: List of content blocks from the document

        Raises:
            NotionNLPError: If there's an error getting document content
        """
        blocks = []
        try:
            has_more = True
            cursor = None

            while has_more:
                params = {
                    "page_size": 100  # Maximum allowed by Notion API
                }
                if cursor:
                    params["start_cursor"] = cursor

                response = requests.get(
                    f"{self.base_url}/blocks/{document_id}/children",
                    headers=self.headers,
                    params=params
                )

                if response.status_code != 200:
                    raise NotionNLPError(f"Failed to get document content: {response.text}")

                data = response.json()
                if not isinstance(data, dict):
                    raise NotionNLPError(f"Invalid response format: {data}")

                # Process blocks
                new_blocks = self._process_blocks(data.get("results", []))
                blocks.extend(new_blocks)

                # Check if there are more blocks to fetch
                has_more = data.get("has_more", False)
                if has_more:
                    cursor = data.get("next_cursor")

            return blocks

        except Exception as e:
            raise NotionNLPError(f"Error getting document content: {str(e)}")

    def _process_blocks(self, blocks_data: List[Dict]) -> List[Block]:
        """Process block data from Notion API response."""
        blocks = []
        current_list_type = None
        list_stack = []  # Track nested lists

        for block in blocks_data:
            try:
                block_type = block["type"]
                content = self._extract_block_content(block)
                indent_level = 0

                # Handle list indentation
                if block_type in ["bulleted_list_item", "numbered_list_item"]:
                    if current_list_type != block_type:
                        # New list type, reset stack
                        list_stack = [block_type]
                        current_list_type = block_type
                        indent_level = 0
                    else:
                        # Continue current list
                        previous_block = blocks[-1] if blocks else None

                        if previous_block and previous_block.type == block_type:
                            if previous_block.has_children:
                                # Increase indent for child items
                                list_stack.append(block_type)
                                indent_level = len(list_stack) - 1
                            elif content.strip().startswith("-") or content.strip().startswith("*"):
                                # Sub-bullet indicator in content
                                indent_level = previous_block.indent_level + 1
                            else:
                                indent_level = previous_block.indent_level
                else:
                    # Non-list block, reset list tracking
                    current_list_type = None
                    list_stack = []

                block_obj = Block(
                    id=block["id"],
                    type=block_type,
                    content=content,
                    has_children=block.get("has_children", False),
                    indent_level=min(indent_level, 3)  # Cap indent level at 3
                )
                blocks.append(block_obj)

                # Handle nested blocks if present
                if block.get("has_children", False):
                    child_blocks = self._get_child_blocks(block["id"])
                    blocks.extend(child_blocks)

            except Exception as e:
                print(f"Warning: Failed to process block {block.get('id', 'unknown')}: {str(e)}")
                continue

        return blocks

    def _extract_block_content(self, block: Dict) -> str:
        """Extract content from a block based on its type."""
        block_type = block["type"]
        content = ""

        try:
            if block_type in block:
                block_data = block[block_type]

                # Handle rich text content
                if "rich_text" in block_data:
                    rich_text = block_data["rich_text"]
                    if isinstance(rich_text, list):
                        content = " ".join(
                            text.get("text", {}).get("content", "")
                            for text in rich_text
                            if isinstance(text, dict)
                        )

                # Handle special block types
                if block_type == "to_do":
                    checked = block_data.get("checked", False)
                    content = f"[{'x' if checked else ' '}] {content}"

        except Exception as e:
            print(f"Warning: Failed to extract content from block: {str(e)}")

        return content.strip()

    def _get_child_blocks(self, block_id: str) -> List[Block]:
        """Retrieve child blocks for a given block ID."""
        try:
            response = requests.get(
                f"{self.base_url}/blocks/{block_id}/children",
                headers=self.headers,
                params={"page_size": 100}
            )

            if response.status_code != 200:
                print(f"Warning: Failed to get child blocks: {response.text}")
                return []

            data = response.json()
            if not isinstance(data, dict) or 'results' not in data:
                return []

            return self._process_blocks(data.get("results", []))

        except Exception as e:
            print(f"Warning: Failed to get child blocks: {str(e)}")
            return []