"""
Notion API client implementation.
"""
from typing import List, Dict, Optional
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
                    # Handle different title property formats
                    title = "Untitled"
                    title_property = page.get("properties", {}).get("title", [])

                    if isinstance(title_property, list) and title_property:
                        title = title_property[0].get("text", {}).get("content", "Untitled")
                    elif isinstance(title_property, dict):
                        title_items = title_property.get("title", [])
                        if title_items and isinstance(title_items, list):
                            title = title_items[0].get("text", {}).get("content", "Untitled")

                    doc = Document(
                        id=page["id"],
                        title=title,
                        created_time=page["created_time"],
                        last_edited_time=page["last_edited_time"]
                    )
                    documents.append(doc)
                except Exception as e:
                    print(f"Warning: Failed to process page {page.get('id', 'unknown')}: {str(e)}")
                    continue

            return documents

        except Exception as e:
            raise NotionNLPError(f"Error listing documents: {str(e)}")

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
        try:
            response = requests.get(
                f"{self.base_url}/blocks/{document_id}/children",
                headers=self.headers
            )

            if response.status_code != 200:
                raise NotionNLPError(f"Failed to get document content: {response.text}")

            data = response.json()
            if not isinstance(data, dict) or 'results' not in data:
                raise NotionNLPError(f"Invalid response format: {data}")

            blocks = []
            for block in data.get("results", []):
                try:
                    block_type = block["type"]
                    content = ""

                    # Extract text content based on block type
                    if block_type in block:
                        rich_text = block[block_type].get("rich_text", [])
                        if rich_text and isinstance(rich_text, list):
                            content = rich_text[0].get("text", {}).get("content", "")

                    blocks.append(Block(
                        id=block["id"],
                        type=block_type,
                        content=content,
                        has_children=block.get("has_children", False)
                    ))
                except Exception as e:
                    print(f"Warning: Failed to process block {block.get('id', 'unknown')}: {str(e)}")
                    continue

            return blocks

        except Exception as e:
            raise NotionNLPError(f"Error getting document content: {str(e)}")

    def _post(self, endpoint: str, json: Dict) -> requests.Response:
        """
        Make a POST request to the Notion API.

        Args:
            endpoint: API endpoint
            json: Request payload

        Returns:
            requests.Response: API response

        Raises:
            NotionNLPError: If the API request fails
        """
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=json
            )
            if response.status_code != 200:
                raise NotionNLPError(f"API request failed: {response.text}")
            return response
        except Exception as e:
            raise NotionNLPError(f"API request failed: {str(e)}")