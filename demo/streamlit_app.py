"""
Streamlit frontend for Notion NLP Library demonstration.
"""
import os
import streamlit as st
from notion_nlp import NotionClient, TextProcessor, DocumentHierarchy, Tagger

# Page config
st.set_page_config(
    page_title="Notion NLP Demo",
    page_icon="📚",
    layout="wide"
)

# Title
st.title("Notion NLP Library Demo")
st.markdown("Explore the core functionalities of the Notion NLP library.")

# Initialize session state
if 'notion_client' not in st.session_state:
    # Get token from environment variable
    notion_token = os.environ.get('NOTION_API_TOKEN')
    if notion_token:
        st.session_state.notion_client = NotionClient(notion_token)
        st.session_state.text_processor = TextProcessor()
        st.session_state.tagger = Tagger()
    else:
        st.error("NOTION_API_TOKEN not found in environment variables!")
        st.stop()

# Create tabs for different functionalities
tab1, tab2, tab3, tab4 = st.tabs([
    "📑 Document List",
    "🌳 Document Hierarchy",
    "🔍 NLP Analysis",
    "🏷️ Document Tagging"
])

# Document List Tab
with tab1:
    st.header("Available Documents")
    
    if st.button("Refresh Documents"):
        with st.spinner("Fetching documents..."):
            try:
                documents = st.session_state.notion_client.list_documents()
                st.session_state.documents = documents
                st.success(f"Found {len(documents)} documents")
                
                # Display documents
                for doc in documents:
                    st.write(f"📄 {doc.title}")
                    if st.button(f"View Content", key=f"view_{doc.id}"):
                        with st.spinner("Fetching content..."):
                            blocks = st.session_state.notion_client.get_document_content(doc.id)
                            st.session_state.current_blocks = blocks
                            for block in blocks:
                                st.text(f"{block.type}: {block.content}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Document Hierarchy Tab
with tab2:
    st.header("Document Structure")
    
    if 'current_blocks' in st.session_state:
        if st.button("Generate Hierarchy"):
            with st.spinner("Building hierarchy..."):
                hierarchy = DocumentHierarchy()
                root = hierarchy.build_hierarchy(st.session_state.current_blocks)
                st.json(hierarchy.to_dict())
    else:
        st.info("Please select a document from the Document List tab first.")

# NLP Analysis Tab
with tab3:
    st.header("NLP Analysis")
    
    if 'current_blocks' in st.session_state:
        if st.button("Analyze Text"):
            with st.spinner("Processing text..."):
                processed = st.session_state.text_processor.process_blocks(st.session_state.current_blocks)
                
                for block in processed:
                    st.subheader(f"Block Analysis")
                    
                    # Display entities
                    st.write("Named Entities:")
                    for entity in block['entities']:
                        st.write(f"- {entity['text']} ({entity['label']})")
                    
                    # Display keywords
                    st.write("Keywords:")
                    st.write(", ".join(block['keywords']))
                    
                    # Display sentences
                    st.write("Sentences:")
                    for sent in block['sentences']:
                        st.write(f"• {sent}")
    else:
        st.info("Please select a document from the Document List tab first.")

# Document Tagging Tab
with tab4:
    st.header("Document Tagging")
    
    if 'current_blocks' in st.session_state:
        # Custom tags input
        custom_tags = st.text_input(
            "Add custom tags (comma-separated)",
            value="important, review, followup"
        )
        
        if st.button("Generate Tags"):
            with st.spinner("Generating tags..."):
                # Add custom tags
                st.session_state.tagger.add_custom_tags(
                    [tag.strip() for tag in custom_tags.split(",")]
                )
                
                # Process each block
                for block in st.session_state.current_blocks:
                    st.subheader(f"Block Tags")
                    st.text(block.content[:100] + "...")
                    
                    # Generate and display tags
                    tags = st.session_state.tagger.generate_tags(block)
                    st.write("Generated Tags:")
                    for tag in tags:
                        st.write(f"- {tag.name} ({tag.type}: {tag.category})")
                    
                    # Analyze and display sentiment
                    sentiment = st.session_state.tagger.analyze_sentiment(block.content)
                    st.write("Sentiment Analysis:")
                    st.progress(sentiment["positive"])
                    st.write(f"Positive: {sentiment['positive']:.2%}")
                    st.write(f"Negative: {sentiment['negative']:.2%}")
    else:
        st.info("Please select a document from the Document List tab first.")
