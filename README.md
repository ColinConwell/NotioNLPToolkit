# Clone the repository
git clone <repository-url>
cd notion-nlp

# Install dependencies
pip install -e .
```

## Quick Start

1. Set up your Notion API token:
```bash
export NOTION_API_TOKEN='your-notion-api-token'
```

2. Share your Notion pages with the integration:
   1. Go to the page you want to analyze in Notion
   2. Click the ••• menu in the top right corner
   3. Select "Add connections"
   4. Find and select your integration from the list
   5. Repeat for each page you want to analyze

3. Run the basic example:
```python
from notion_nlp import NotionClient, TextProcessor, Tagger

# Initialize clients
client = NotionClient(os.environ['NOTION_API_TOKEN'])
processor = TextProcessor()
tagger = Tagger()

# List and process documents
documents = client.list_documents()
for doc in documents:
    blocks = client.get_document_content(doc.id)
    processed = processor.process_blocks(blocks)
    tags = [tagger.generate_tags(block) for block in blocks]
```

## Interactive Demo

Launch the interactive Streamlit demo:

```bash
./launch.sh --port 8501
```

Or run with test validation:

```bash
./launch.sh --stop-on-error --port 8501
```

## Development

### Running Tests

```bash
python -m pytest tests/