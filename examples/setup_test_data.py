"""
Helper script to create test data in Notion for testing the Notion NLP library.
"""
import os
from notion_nlp import NotionClient
from notion_nlp.exceptions import NotionNLPError

def create_test_page(client: NotionClient) -> str:
    """Create a test page with sufficient content for testing."""
    try:
        # Create a new page with test content
        page_data = {
            "parent": {"type": "workspace", "workspace": True},
            "properties": {
                "title": [{"text": {"content": "Notion NLP Test Document"}}]
            },
            "children": [
                {
                    "object": "block",
                    "type": "heading_1",
                    "heading_1": {
                        "text": [{"text": {"content": "Testing Document Structure"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"text": {"content": "This is a test document created for the Notion NLP library testing purposes."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "text": [{"text": {"content": "Sample Content Section"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"text": {"content": "John works at Apple Inc. in California. The company is known for its innovative technology products."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "text": [{"text": {"content": "Analysis Section"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"text": {"content": "This document contains various types of content for testing NLP capabilities including named entities, sentiment analysis, and summarization features."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "text": [{"text": {"content": "Technical Details"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"text": {"content": "The system uses advanced natural language processing techniques to analyze document content and structure."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"text": {"content": "We're using spaCy for NLP tasks and implementing custom algorithms for document hierarchy analysis."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {
                        "text": [{"text": {"content": "Test Scenarios"}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"text": {"content": "This is an important document that needs review. The content is specifically crafted to test various features including custom tag detection."}}]
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "text": [{"text": {"content": "The quick brown fox jumps over the lazy dog. This sentence is included to test basic NLP processing capabilities."}}]
                    }
                }
            ]
        }
        
        response = client._post("pages", json=page_data)
        if response.status_code == 200:
            return response.json()["id"]
        else:
            raise NotionNLPError(f"Failed to create test page: {response.text}")
            
    except Exception as e:
        raise NotionNLPError(f"Error creating test data: {str(e)}")

def main():
    """Main function to set up test data."""
    try:
        notion_token = os.environ.get('NOTION_API_TOKEN')
        if not notion_token:
            raise NotionNLPError("NOTION_API_TOKEN not found in environment variables")
        
        print("Initializing Notion client...")
        client = NotionClient(notion_token)
        
        print("\nCreating test document...")
        page_id = create_test_page(client)
        print(f"Test document created successfully! Page ID: {page_id}")
        print("\nYou can now run the test_functionality.py script to test the library.")
        
    except NotionNLPError as e:
        print(f"Setup error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
