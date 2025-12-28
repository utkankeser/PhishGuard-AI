"""
RAG-based Phishing Email Analyzer for PhishGuard AI.
Analyzes emails against company-specific rules using Retrieval-Augmented Generation.
"""

import os
import sys
import argparse
import json
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import get_config, set_api_key
from logger import get_logger
from exceptions import VectorStoreError, LLMError, ConfigurationError

# Initialize logger
logger = get_logger(__name__)


def load_vector_store(config) -> FAISS:
    """
    Load the FAISS vector database.
    
    Args:
        config: Configuration object
        
    Returns:
        FAISS vector store instance
        
    Raises:
        VectorStoreError: If database cannot be loaded
    """
    try:
        logger.info("Loading vector database...")
        embeddings = HuggingFaceEmbeddings(model_name=config.embedding_model_name)
        vector_store = FAISS.load_local(
            config.vector_db_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"✅ Vector database loaded successfully from {config.vector_db_path}")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to load vector database: {e}")
        raise VectorStoreError(
            "Could not load vector database",
            f"Make sure you've run 'python rag_setup.py' first. Error: {str(e)}"
        )


def initialize_llm(config) -> ChatGroq:
    """
    Initialize the LLM model.
    
    Args:
        config: Configuration object
        
    Returns:
        ChatGroq instance
        
    Raises:
        LLMError: If LLM cannot be initialized
    """
    try:
        logger.info(f"Initializing LLM: {config.llm_model_name}")
        
        # Ensure API key is set
        if config.groq_api_key:
            os.environ["GROQ_API_KEY"] = config.groq_api_key
        
        llm = ChatGroq(
            model=config.llm_model_name,
            temperature=config.llm_temperature
        )
        logger.info("✅ LLM initialized successfully")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise LLMError(
            "Could not initialize LLM",
            f"Check your API key and internet connection. Error: {str(e)}"
        )


def analyze_email(email_content: str, config, vector_store: FAISS, llm: ChatGroq) -> Dict[str, Any]:
    """
    Analyze an email for phishing using RAG.
    
    Args:
        email_content: The email text to analyze
        config: Configuration object
        vector_store: FAISS vector database
        llm: ChatGroq LLM instance
        
    Returns:
        Dictionary with analysis results
    """
    logger.info("Starting email analysis...")
    
    # Retrieve relevant rules from vector database
    logger.debug(f"Searching for top {config.rag_top_k} relevant rules...")
    relevant_docs = vector_store.similarity_search(email_content, k=config.rag_top_k)
    
    # Combine retrieved rules
    context_text = "\n".join([doc.page_content for doc in relevant_docs])
    logger.info(f"Found {len(relevant_docs)} relevant company rules")
    logger.debug(f"Retrieved rules:\n{context_text}")
    
    # Create the analysis prompt
    system_prompt = """
You are a Senior Cyber Security Analyst for a specific company.
Use the following COMPANY RULES (Context) to analyze the email.

CONTEXT (Company Rules):
{context}

INSTRUCTIONS:
1. First, check if the email violates any of the specific COMPANY RULES in the context.
2. If it violates a rule, explicitly cite it (e.g., "Violates Rule #1").
3. Then check for general phishing indicators.
4. If the email contains <email> tags, only analyze the content inside them.
5. Provide a clear verdict: SAFE or PHISHING DETECTED.
"""
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "<email>\n{email_icerigi}\n</email>")
    ])
    
    # Run the analysis
    chain = prompt_template | llm
    logger.info("Sending request to LLM...")
    
    try:
        result = chain.invoke({
            "context": context_text,
            "email_icerigi": email_content
        })
        logger.info("✅ Analysis completed successfully")
        
        return {
            "email": email_content,
            "analysis": result.content,
            "relevant_rules": [doc.page_content for doc in relevant_docs],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise LLMError("Email analysis failed", str(e))


def main():
    """Main entry point for the RAG phishing analyzer."""
    parser = argparse.ArgumentParser(description="PhishGuard AI - RAG Email Analyzer")
    parser.add_argument(
        "--email",
        type=str,
        help="Email content to analyze (or use default test email)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="Groq API key (overrides environment variable)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = get_config()
        logger.info("PhishGuard AI - RAG Email Analyzer")
        logger.info("=" * 50)
        
        # Override API key if provided
        if args.api_key:
            set_api_key(args.api_key)
            logger.info("Using API key from command line")
        
        # Validate API key
        config.validate_api_key()
        
        # Load vector store
        vector_store = load_vector_store(config)
        
        # Initialize LLM
        llm = initialize_llm(config)
        
        # Use provided email or default test email
        email_content = args.email or """From: CEO (ceo@urgent-company-update.com)
Subject: Confidential Transfer

Dear Employee,
I am in a meeting and cannot talk. 
I need you to process a wire transfer of $60,000 to our vendor immediately.
This is an exception to the normal procedure. Do not tell anyone."""
        
        if not args.email:
            logger.info("Using default test email (use --email to provide custom email)")
        
        # Analyze the email
        result = analyze_email(email_content, config, vector_store, llm)
        
        # Output results
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 50)
            print("🔍 RELEVANT COMPANY RULES:")
            print("=" * 50)
            for i, rule in enumerate(result["relevant_rules"], 1):
                print(f"\n{i}. {rule}")
            
            print("\n" + "=" * 50)
            print("🤖 ANALYSIS RESULT:")
            print("=" * 50)
            print(result["analysis"])
            print("\n" + "=" * 50)
        
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        sys.exit(1)
    except VectorStoreError as e:
        logger.error(f"Vector store error: {e}")
        print(f"\n❌ Vector Database Error: {e}", file=sys.stderr)
        sys.exit(1)
    except LLMError as e:
        logger.error(f"LLM error: {e}")
        print(f"\n❌ LLM Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n❌ Unexpected Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()