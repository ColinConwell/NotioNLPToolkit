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
            return response.status_code == 200
        except Exception as e:
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def list_documents(self) -> List[Document]:
        """
        List all available documents.

        Returns:
            List[Document]: List of document objects
        """
        try:
            response = requests.post(
                f"{self.base_url}/search",
                headers=self.headers,
                json={"filter": {"property": "object", "value": "page"}}
            )

            if response.status_code != 200:
                raise NotionNLPError(f"Failed to list documents: {response.text}")

            results = response.json().get("results", [])
            return [Document(
                id=page["id"],
                title=page["properties"].get("title", [{}])[0].get("text", {}).get("content", "Untitled"),
                created_time=page["created_time"],
                last_edited_time=page["last_edited_time"]
            ) for page in results]

        except Exception as e:
            raise NotionNLPError(f"Error listing documents: {str(e)}")

    def get_document_content(self, document_id: str) -> List[Block]:
        """
        Retrieve the content of a specific document.

        Args:
            document_id: The ID of the document to retrieve

        Returns:
            List[Block]: List of content blocks from the document
        """
        try:
            response = requests.get(
                f"{self.base_url}/blocks/{document_id}/children",
                headers=self.headers
            )

            if response.status_code != 200:
                raise NotionNLPError(f"Failed to get document content: {response.text}")

            blocks = response.json().get("results", [])
            return [Block(
                id=block["id"],
                type=block["type"],
                content=block[block["type"]]["text"][0]["plain_text"] if "text" in block[block["type"]] else "",
                has_children=block.get("has_children", False)
            ) for block in blocks]

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
        """
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=json
            )
            return response
        except Exception as e:
            raise NotionNLPError(f"API request failed: {str(e)}")