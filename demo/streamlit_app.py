import os
import logging
import streamlit as st
from notion_nlp import NotionClient, TextProcessor, DocumentHierarchy, Tagger
from notion_nlp.exceptions import AuthenticationError, NotionNLPError

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title="Notion NLP Demo",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger.info("Starting Notion NLP Demo application")

# Initialize session state for storing objects
if 'initialized' not in st.session_state:
    logger.info("Initializing session state")
    st.session_state.initialized = False
    st.session_state.documents = None
    st.session_state.current_blocks = None
    st.session_state.selected_doc_id = None

# Initialize clients if API token is available
notion_token = os.environ.get('NOTION_API_TOKEN')
logger.debug(f"Notion API token present: {notion_token is not None}")

if notion_token and not st.session_state.initialized:
    try:
        logger.info("Attempting to initialize Notion client")
        st.session_state.notion_client = NotionClient(notion_token)
        logger.info("Notion client initialized successfully")

        logger.info("Initializing text processor")
        st.session_state.text_processor = TextProcessor()
        logger.info("Text processor initialized")

        logger.info("Initializing tagger")
        st.session_state.tagger = Tagger()
        logger.info("Tagger initialized")

        st.session_state.initialized = True
        logger.info("All components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize clients: {str(e)}", exc_info=True)
        st.error(f"Failed to initialize clients: {str(e)}")

# Title and description
st.title("Notion NLP Library Demo")
st.markdown("""
This demo showcases the core functionalities of the Notion NLP library:
- Document listing and content retrieval
- Hierarchical document structure analysis
- Natural Language Processing capabilities
- Automated document tagging
""")

# Main content
if st.session_state.initialized:
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📑 Document List",
        "🌳 Document Hierarchy",
        "🔍 NLP Analysis",
        "🏷️ Document Tagging"
    ])

    # Document List Tab
    with tab1:
        st.header("Available Documents")

        # Document list and content view columns
        col_list, col_content = st.columns([1, 2])

        with col_list:
            if st.button("🔄 Refresh Documents"):
                try:
                    with st.spinner("Fetching documents..."):
                        documents = st.session_state.notion_client.list_documents()
                        st.session_state.documents = documents
                        st.success(f"Found {len(documents)} documents")
                except AuthenticationError:
                    st.error("Authentication failed. Please check your Notion API token.")
                except Exception as e:
                    st.error(f"Error fetching documents: {str(e)}")

            if st.session_state.documents:
                st.subheader("Select a Document")
                for doc in st.session_state.documents:
                    # Create a button for each document
                    button_style = "primary" if doc.id == st.session_state.selected_doc_id else "secondary"
                    if st.button(
                        f"📄 {doc.title}",
                        key=f"view_{doc.id}",
                        type=button_style,
                    ):
                        try:
                            with st.spinner("Fetching content..."):
                                blocks = st.session_state.notion_client.get_document_content(doc.id)
                                st.session_state.current_blocks = blocks
                                st.session_state.selected_doc_id = doc.id
                                st.success("Content loaded successfully")
                        except Exception as e:
                            st.error(f"Error loading content: {str(e)}")
                            st.session_state.current_blocks = None
                            st.session_state.selected_doc_id = None

        # Content viewing area
        with col_content:
            if st.session_state.current_blocks and st.session_state.selected_doc_id:
                st.subheader("Document Content")

                # Display selected document title with improved styling
                selected_doc = next(
                    (doc for doc in st.session_state.documents if doc.id == st.session_state.selected_doc_id),
                    None
                )
                if selected_doc:
                    st.markdown("""
                    <div style='padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem; margin-bottom: 1rem;'>
                        <h3 style='margin: 0;'>📄 {}</h3>
                    </div>
                    """.format(selected_doc.title), unsafe_allow_html=True)

                    # Add content statistics
                    total_blocks = len(st.session_state.current_blocks)
                    st.markdown(f"**Total blocks:** {total_blocks}")

                    # Display content in a scrollable container with improved formatting
                    content_container = st.container()
                    with content_container:
                        for block in st.session_state.current_blocks:
                            if block.type == "paragraph":
                                st.write(block.content)
                            elif block.type == "heading_1":
                                st.markdown(f"<h1>{block.content}</h1>", unsafe_allow_html=True)
                            elif block.type == "heading_2":
                                st.markdown(f"<h2>{block.content}</h2>", unsafe_allow_html=True)
                            elif block.type == "heading_3":
                                st.markdown(f"<h3>{block.content}</h3>", unsafe_allow_html=True)
                            elif block.type == "bulleted_list_item":
                                st.markdown(f"<li>{block.content}</li>", unsafe_allow_html=True)
                            elif block.type == "numbered_list_item":
                                st.markdown(f"<li>{block.content}</li>", unsafe_allow_html=True)
                            elif block.type == "code":
                                st.code(block.content)
                            elif block.type == "quote":
                                st.markdown(f"> {block.content}")
                            else:
                                st.text(block.content)
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