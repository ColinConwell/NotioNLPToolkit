# Notion NLP Library

A Python library for processing Notion documents with advanced NLP capabilities, featuring a Streamlit-based interactive frontend for document exploration and analysis.

## Features

- **Notion Integration**: Seamless access to Notion documents through the official API
- **Advanced NLP Processing**: 
  - Named Entity Recognition
  - Keyword Extraction
  - Text Summarization
  - Sentiment Analysis
- **Document Structure Analysis**: Hierarchical organization of document content
- **Automated Tagging**: Smart tag generation based on content analysis
- **Interactive Frontend**: Streamlit-based UI for document exploration

## Installation

```bash
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

2. Run the basic example:
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
```

### Project Structure

- `notion_nlp/`: Core library implementation
  - `notion_client.py`: Notion API integration
  - `text_processor.py`: NLP processing capabilities
  - `hierarchy.py`: Document structure analysis
  - `tags.py`: Automated tagging system
  - `models.py`: Data models
- `demo/`: Interactive frontend
  - `streamlit_app.py`: Streamlit application
  - `notion_nlp_demo.ipynb`: Jupyter notebook demo
- `tests/`: Test suite
- `examples/`: Usage examples

## Features in Detail

### Document Processing

The library processes Notion documents through several stages:

1. **Content Retrieval**: Fetch document content via Notion API
2. **Structure Analysis**: Build hierarchical representation of document structure
3. **NLP Processing**: Apply NLP techniques for content analysis
4. **Tag Generation**: Generate relevant tags based on content

### NLP Capabilities

- **Entity Recognition**: Identify and classify named entities (people, organizations, locations)
- **Keyword Extraction**: Extract significant terms and phrases
- **Text Summarization**: Generate concise summaries of document content
- **Sentiment Analysis**: Analyze emotional tone of content

### Interactive Frontend

The Streamlit frontend provides:

- Document listing and navigation
- Visual representation of document hierarchy
- NLP analysis results visualization
- Interactive tag management
- Real-time content processing

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
