import os
import logging
import streamlit as st
from notion_nlp import NotionClient, TextProcessor, DocumentHierarchy, Tagger
from notion_nlp.exceptions import AuthenticationError, NotionNLPError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Notion NLP Demo",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for storing objects
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.documents = None
    st.session_state.current_blocks = None
    st.session_state.selected_doc_id = None

# Title and description
st.title("Notion NLP Library Demo")
st.markdown("""
This demo showcases the core functionalities of the Notion NLP library:
- Document listing and content retrieval
- Hierarchical document structure analysis
- Natural Language Processing capabilities
- Automated document tagging
""")

# Initialize clients if API token is available
notion_token = os.environ.get('NOTION_API_TOKEN')
if notion_token and not st.session_state.initialized:
    try:
        st.session_state.notion_client = NotionClient(notion_token)
        st.session_state.text_processor = TextProcessor()
        st.session_state.tagger = Tagger()
        st.session_state.initialized = True
    except Exception as e:
        st.error(f"Failed to initialize clients: {str(e)}")

# Main content
if st.session_state.initialized:
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📑 Document List",
        "🌳 Document Hierarchy",
        "🔍 NLP Analysis",
        "🏷️ Document Tagging"
    ])

    @st.cache_data
    def get_document_style():
        return """
        <style>
        /* Remove the document-list class since we'll style the buttons directly */
        .stButton > button {
            background-color: white;
            color: black;
            width: 100%;
            margin-bottom: 5px;
            text-align: left;
            transition: background-color 0.3s ease;
        }
        .stButton > button[data-selected="true"] {
            background-color: #90EE90 !important;
            color: black !important;
            font-weight: bold;
        }
        .content-view {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 5px;
            margin: 10px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .bullet-list {
            margin-left: 20px;
        }
        .sub-bullet {
            margin-left: 40px;
        }
        </style>
        """

    # Document List Tab section
    with tab1:
        st.header("Available Documents")
        st.markdown(get_document_style(), unsafe_allow_html=True)

        # Use columns with specified ratios
        col_list, col_content = st.columns([1, 5])

        with col_list:
            if st.button("🔄 Refresh Documents", use_container_width=True):
                try:
                    with st.spinner("Fetching documents..."):
                        documents = st.session_state.notion_client.list_documents()
                        st.session_state.documents = documents
                        st.success(f"Found {len(documents)} documents")
                except Exception as e:
                    st.error(f"Error fetching documents: {str(e)}")

            if st.session_state.documents:
                st.subheader("Select a Document")
                for doc in st.session_state.documents:
                    # Create styled button for each document
                    button_label = f"📄 {doc.title}"
                    if st.button(
                        button_label,
                        key=f"doc_{doc.id}",
                        help=f"Last edited: {doc.last_edited_time}",
                        use_container_width=True,
                        type="secondary" if doc.id != st.session_state.selected_doc_id else "primary",
                    ):
                        try:
                            with st.spinner("Fetching content..."):
                                blocks = st.session_state.notion_client.get_document_content(doc.id)
                                st.session_state.current_blocks = blocks
                                st.session_state.selected_doc_id = doc.id
                        except Exception as e:
                            st.error(f"Error loading content: {str(e)}")
                            st.session_state.current_blocks = None
                            st.session_state.selected_doc_id = None


        # Content viewing area
        with col_content:
            if st.session_state.current_blocks and st.session_state.selected_doc_id:

                # Display selected document title
                selected_doc = next(
                    (doc for doc in st.session_state.documents if doc.id == st.session_state.selected_doc_id),
                    None
                )
                if selected_doc:
                    st.markdown(f"### 📄 {selected_doc.title}")

                # Display content with improved formatting
                content_container = st.container()
                with content_container:
                    for block in st.session_state.current_blocks:
                        if block.type == "paragraph":
                            st.write(block.content)
                        elif block.type.startswith("heading"):
                            level = int(block.type[-1])
                            st.markdown(f"{'#' * level} {block.content}")
                        elif block.type in ["bulleted_list_item", "numbered_list_item"]:
                            indent = "  " * block.indent_level
                            bullet = "•" if block.type == "bulleted_list_item" else f"{block.indent_level + 1}."
                            st.markdown(
                                f'<div class="bullet-list{" sub-bullet" if block.indent_level > 0 else ""}">'
                                f'{indent}{bullet} {block.content}'
                                '</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            st.write(block.content)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Select a document from the list to view its content")

    # Document Hierarchy Tab
    with tab2:
        st.header("Document Structure")

        if st.session_state.current_blocks:
            if st.button("🔄 Generate Hierarchy"):
                with st.spinner("Building hierarchy..."):
                    try:
                        hierarchy = DocumentHierarchy()
                        root = hierarchy.build_hierarchy(st.session_state.current_blocks)
                        st.json(hierarchy.to_dict())
                    except Exception as e:
                        st.error(f"Error building hierarchy: {str(e)}")
        else:
            st.info("Please select a document from the Document List tab first.")

    # NLP Analysis Tab
    with tab3:
        st.header("NLP Analysis")

        if st.session_state.current_blocks:
            if st.button("🔍 Analyze Text"):
                with st.spinner("Processing text..."):
                    try:
                        processed = st.session_state.text_processor.process_blocks(st.session_state.current_blocks)

                        for block in processed:
                            with st.expander(f"Analysis for: {block['content'][:50]}..."):
                                # Named Entities
                                st.subheader("🏷️ Named Entities")
                                for entity in block['entities']:
                                    st.write(f"- {entity['text']} ({entity['label']})")

                                # Keywords
                                st.subheader("🔑 Keywords")
                                st.write(", ".join(block['keywords']))

                                # Sentences
                                st.subheader("📝 Sentences")
                                for sent in block['sentences']:
                                    st.write(f"• {sent}")
                    except Exception as e:
                        st.error(f"Error analyzing text: {str(e)}")
        else:
            st.info("Please select a document from the Document List tab first.")

    # Document Tagging Tab
    with tab4:
        st.header("Document Tagging")

        if st.session_state.current_blocks:
            custom_tags = st.text_input(
                "Add custom tags (comma-separated)",
                value="important, review, followup"
            )

            if st.button("🏷️ Generate Tags"):
                with st.spinner("Generating tags..."):
                    try:
                        # Add custom tags
                        st.session_state.tagger.add_custom_tags(
                            [tag.strip() for tag in custom_tags.split(",")]
                        )

                        # Process each block
                        for block in st.session_state.current_blocks:
                            with st.expander(f"Tags for: {block.content[:50]}..."):
                                # Generate and display tags
                                tags = st.session_state.tagger.generate_tags(block)
                                st.subheader("Generated Tags")
                                for tag in tags:
                                    st.write(f"- {tag.name} ({tag.type}: {tag.category})")

                                # Analyze and display sentiment
                                sentiment = st.session_state.tagger.analyze_sentiment(block.content)
                                st.subheader("Sentiment Analysis")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric("Positive", f"{sentiment['positive']:.1%}")
                                with col2:
                                    st.metric("Negative", f"{sentiment['negative']:.1%}")
                    except Exception as e:
                        st.error(f"Error generating tags: {str(e)}")
        else:
            st.info("Please select a document from the Document List tab first.")
else:
    st.error("Notion API token not found. Please ensure the NOTION_API_TOKEN environment variable is set.")