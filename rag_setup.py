"""
Vector Database Setup for PhishGuard AI.
Creates and saves a FAISS vector database with company security policies.
"""

from pathlib import Path
from typing import List
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import get_config
from logger import get_logger
from exceptions import VectorStoreError, EmbeddingError

# Initialize logger
logger = get_logger(__name__)


def get_company_policies() -> List[str]:
    """
    Get the list of company security policies.
    In production, this would load from a database or PDF files.
    
    Returns:
        List of policy strings
    """
    policies = [
        "RULE 1: The company CEO never requests wire transfers via email. This is strictly prohibited.",
        "RULE 2: The IT Support team will never ask you to reset your password by clicking a link.",
        "RULE 3: Emergency drills are only announced from 'security@company.com' address.",
        "RULE 4: Payments over $50,000 require a wet signature; email is not sufficient."
    ]
    logger.info(f"Loaded {len(policies)} company policies")
    return policies


def create_embeddings(model_name: str) -> HuggingFaceEmbeddings:
    """
    Create embedding model instance.
    
    Args:
        model_name: Name of the HuggingFace model
        
    Returns:
        HuggingFaceEmbeddings instance
        
    Raises:
        EmbeddingError: If model cannot be loaded
    """
    try:
        logger.info(f"Loading embedding model: {model_name}")
        logger.info("This may take a few minutes on first run (downloading model)...")
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        logger.info("✅ Embedding model loaded successfully")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        raise EmbeddingError(
            "Could not load embedding model",
            f"Check your internet connection and disk space. Error: {str(e)}"
        )


def create_vector_store(
    texts: List[str],
    embeddings: HuggingFaceEmbeddings,
    save_path: str
) -> FAISS:
    """
    Create and save FAISS vector database.
    
    Args:
        texts: List of text documents to embed
        embeddings: Embedding model instance
        save_path: Path to save the database
        
    Returns:
        FAISS vector store instance
        
    Raises:
        VectorStoreError: If database cannot be created
    """
    try:
        logger.info("Creating vector database from documents...")
        vector_store = FAISS.from_texts(texts, embeddings)
        
        # Save to disk
        logger.info(f"Saving vector database to: {save_path}")
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        vector_store.save_local(save_path)
        
        logger.info(f"✅ Vector database saved successfully to '{save_path}'")
        return vector_store
    except Exception as e:
        logger.error(f"Failed to create vector database: {e}")
        raise VectorStoreError(
            "Could not create vector database",
            f"Error: {str(e)}"
        )


def validate_vector_store(vector_store: FAISS, sample_query: str = "CEO para transferi"):
    """
    Validate the vector store by performing a test search.
    
    Args:
        vector_store: FAISS vector store to validate
        sample_query: Test query string
    """
    try:
        logger.info("Validating vector database with test query...")
        results = vector_store.similarity_search(sample_query, k=1)
        if results:
            logger.info(f"✅ Validation successful! Found {len(results)} result(s)")
            logger.debug(f"Sample result: {results[0].page_content[:100]}...")
        else:
            logger.warning("⚠️ Validation returned no results")
    except Exception as e:
        logger.error(f"Validation failed: {e}")


def main():
    """Main entry point for vector database setup."""
    try:
        logger.info("=" * 60)
        logger.info("PhishGuard AI - Vector Database Setup")
        logger.info("=" * 60)
        
        # Load configuration
        config = get_config()
        logger.info(f"Using embedding model: {config.embedding_model_name}")
        logger.info(f"Database will be saved to: {config.vector_db_path}")
        
        # Get company policies
        policies = get_company_policies()
        
        # Create embeddings
        embeddings = create_embeddings(config.embedding_model_name)
        
        # Create and save vector store
        vector_store = create_vector_store(
            texts=policies,
            embeddings=embeddings,
            save_path=config.vector_db_path
        )
        
        # Validate the database
        validate_vector_store(vector_store)
        
        logger.info("=" * 60)
        logger.info("✅ Setup Complete!")
        logger.info("=" * 60)
        logger.info("You can now run:")
        logger.info("  - python phish_guard_rag.py (for CLI analysis)")
        logger.info("  - streamlit run app.py (for web interface)")
        
    except (VectorStoreError, EmbeddingError) as e:
        logger.error(f"Setup failed: {e}")
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        logger.exception("Unexpected error during setup")
        print(f"\n❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())