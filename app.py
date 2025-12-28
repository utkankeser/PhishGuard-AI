"""
PhishGuard AI - Streamlit Web Application
Production-ready web interface for phishing email analysis using RAG.
"""

import streamlit as st
import os
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import get_config, set_api_key
from logger import get_logger
from exceptions import VectorStoreError, LLMError, ConfigurationError

# Initialize logger
logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="PhishGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .header-subtitle {
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_vector_store_cached(_config):
    """
    Load vector store with caching for performance.
    Uses underscore prefix to prevent hashing issues with Streamlit.
    """
    try:
        logger.info("Loading vector database (cached)...")
        embeddings = HuggingFaceEmbeddings(model_name=_config.embedding_model_name)
        vector_store = FAISS.load_local(
            _config.vector_db_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info("✅ Vector database loaded successfully")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to load vector database: {e}")
        raise VectorStoreError(
            "Could not load vector database",
            f"Make sure you've run 'python rag_setup.py' first. Error: {str(e)}"
        )


def initialize_llm(_config, api_key: str) -> ChatGroq:
    """Initialize LLM with provided API key."""
    try:
        logger.info(f"Initializing LLM: {_config.llm_model_name}")
        os.environ["GROQ_API_KEY"] = api_key
        
        llm = ChatGroq(
            model=_config.llm_model_name,
            temperature=_config.llm_temperature
        )
        logger.info("✅ LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise LLMError(
            "Could not initialize LLM",
            f"Check your API key and internet connection. Error: {str(e)}"
        )


def analyze_email(email_content: str, config, vector_store: FAISS, llm: ChatGroq):
    """Analyze email using RAG pipeline."""
    logger.info("Starting email analysis via Streamlit app...")
    
    # Retrieve relevant rules
    logger.debug(f"Searching for top {config.rag_top_k} relevant rules...")
    docs = vector_store.similarity_search(email_content, k=config.rag_top_k)
    context_text = "\n".join([d.page_content for d in docs])
    
    logger.info(f"Found {len(docs)} relevant company rules")
    
    # Create prompt
    system_prompt = """
You are a Senior Cyber Security Analyst.
Use the following COMPANY RULES (Context) to analyze the email.

CONTEXT:
{context}

INSTRUCTIONS:
1. First check if it violates specific COMPANY RULES. Cite them.
2. Then check for general phishing indicators.
3. Reply in clear Markdown format with:
   - **Verdict**: SAFE or PHISHING DETECTED
   - **Risk Level**: Low/Medium/High/Critical
   - **Analysis**: Detailed explanation
   - **Recommendations**: What action to take
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "<email>\n{email_icerigi}\n</email>")
    ])
    
    # Execute analysis
    chain = prompt | llm
    logger.info("Sending request to LLM...")
    
    result = chain.invoke({
        "context": context_text,
        "email_icerigi": email_content
    })
    
    logger.info("✅ Analysis completed successfully")
    
    return result.content, context_text, docs


# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092663.png", width=100)
    st.title("🛡️ PhishGuard AI")
    st.markdown("**Corporate Email Security Analyst**")
    st.markdown("---")
    
    # Load config
    try:
        config = get_config()
        
        # API Key Management
        st.subheader("⚙️ Settings")
        
        # Check if API key exists in environment
        env_api_key = config.groq_api_key if config.groq_api_key and config.groq_api_key != "your_groq_api_key_here" else ""
        
        if env_api_key:
            st.success("✅ API Key loaded from environment")
            api_key = env_api_key
            show_input = st.checkbox("Override with different key")
            if show_input:
                api_key = st.text_input(
                    "Groq API Key",
                    type="password",
                    placeholder="gsk_...",
                    help="Enter your Groq API key"
                )
        else:
            api_key = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_...",
                help="Enter your Groq API key or set GROQ_API_KEY in .env file"
            )
        
        st.markdown("---")
        
        # System Status
        st.subheader("📊 System Status")
        
        # Check vector database
        try:
            vector_store = load_vector_store_cached(config)
            st.success("✅ Vector DB: Loaded")
        except Exception as e:
            st.error("❌ Vector DB: Not Found")
            st.warning("Run: `python rag_setup.py`")
            vector_store = None
        
        # Model info
        st.info(f"**Model**: {config.llm_model_name}")
        st.info(f"**Embeddings**: {config.embedding_model_name.split('/')[-1]}")
        
        st.markdown("---")
        
        # Info section
        with st.expander("ℹ️ How It Works"):
            st.markdown("""
            **PhishGuard AI** learns your company rules and 
            analyzes emails accordingly.
            
            **Technology**:
            - 🧠 LLM: Llama 3.3 (70B)
            - 📚 RAG: FAISS Vector DB
            - 🎯 Retrieval-Augmented Generation
            
            **Features**:
            - Analysis based on company rules
            - General phishing indicators
            - Risk level assessment
            - Action recommendations
            """)
        
    except Exception as e:
        st.error(f"⚠️ Configuration error: {e}")
        logger.error(f"Sidebar configuration error: {e}")

# --- MAIN AREA ---
st.header("🛡️ Email Security Analysis")
st.markdown('<p class="header-subtitle">Paste the suspicious email below, and let AI analyze it according to company rules.</p>', unsafe_allow_html=True)

# Email input
email_input = st.text_area(
    "Email Content:",
    height=250,
    placeholder="""From: sender@example.com
Subject: Urgent Action Required

Hi Team,
Please click the link below to verify your account...
""",
    help="Paste the email subject and content here"
)

# Analysis button
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    analyze_button = st.button("🚀 ANALYZE", type="primary", use_container_width=True)
with col2:
    if st.button("🗑️ Clear", use_container_width=True):
        st.rerun()

if analyze_button:
    # Validation
    if not api_key:
        st.error("❌ Please enter your API Key in the left menu or configure it in .env file!")
        logger.warning("Analysis attempted without API key")
        st.stop()
    
    if not email_input or len(email_input.strip()) < 10:
        st.warning("⚠️ Please enter an email text to analyze.")
        logger.warning("Analysis attempted with empty/short email")
        st.stop()
    
    if vector_store is None:
        st.error("❌ Vector database could not be loaded. Please run `python rag_setup.py` first.")
        st.stop()
    
    # Perform analysis
    with st.spinner("🔍 Scanning database and analyzing..."):
        try:
            logger.info(f"Starting analysis for email of length {len(email_input)}")
            
            # Initialize LLM
            llm = initialize_llm(config, api_key)
            
            # Analyze
            analysis_result, context_text, relevant_docs = analyze_email(
                email_input,
                config,
                vector_store,
                llm
            )
            
            # Display results
            st.success("✅ Analysis Complete!")
            
            # Results in columns
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📝 AI Analysis Report")
                st.markdown(analysis_result)
                
                # Quick actions
                st.markdown("---")
                st.markdown("**📋 Quick Actions:**")
                action_col1, action_col2, action_col3 = st.columns(3)
                with action_col1:
                    if st.button("🚫 Quarantine", use_container_width=True):
                        st.info("Quarantine feature coming soon!")
                with action_col2:
                    if st.button("✉️ Report", use_container_width=True):
                        st.info("Reporting feature coming soon!")
                with action_col3:
                    if st.button("📥 Export PDF", use_container_width=True):
                        st.info("PDF export coming soon!")
            
            with col2:
                st.subheader("📚 Related Rules")
                st.info("Company rules used in analysis:")
                
                for i, doc in enumerate(relevant_docs, 1):
                    with st.expander(f"Rule {i}", expanded=True):
                        st.markdown(doc.page_content)
                
                # Metadata
                st.markdown("---")
                st.markdown("**📊 Analysis Metadata:**")
                st.caption(f"Model: {config.llm_model_name}")
                st.caption(f"Rules: {len(relevant_docs)}")
                st.caption(f"Email length: {len(email_input)} characters")
            
            logger.info("Analysis results displayed successfully")
            
        except ConfigurationError as e:
            st.error(f"❌ Configuration Error: {e}")
            logger.error(f"Configuration error during analysis: {e}")
        except VectorStoreError as e:
            st.error(f"❌ Database Error: {e}")
            st.info("💡 Tip: Run `python rag_setup.py` in the terminal.")
            logger.error(f"Vector store error during analysis: {e}")
        except LLMError as e:
            st.error(f"❌ LLM Error: {e}")
            st.info("💡 Tip: Check your API key and internet connection.")
            logger.error(f"LLM error during analysis: {e}")
        except Exception as e:
            st.error(f"❌ Unexpected Error: {e}")
            st.info("💡 Please check the logs or restart the project.")
            logger.exception("Unexpected error during analysis")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>PhishGuard AI | Powered by Llama 3.3 & RAG Technology</p>
        <p style='font-size: 0.8rem;'>Version 2.0 | Production Ready</p>
    </div>
    """,
    unsafe_allow_html=True
)