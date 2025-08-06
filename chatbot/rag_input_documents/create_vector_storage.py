"""
Vector Storage Creation Script for RAG Documents

This script processes documents from various formats (CSV, PDF, Markdown) and creates
a ChromaDB vector storage for efficient retrieval in the RAG pipeline.
"""

import os
import logging
import shutil
import hashlib
import json
from pathlib import Path
from typing import List
import pandas as pd
from dotenv import load_dotenv

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    return api_key

def load_markdown_documents(markdown_dir: Path) -> List[Document]:
    """Load and process markdown documents"""
    documents = []
    markdown_files = list(markdown_dir.glob("*.md"))
    
    logger.info(f"Found {len(markdown_files)} markdown files")
    
    for md_file in markdown_files:
        try:
            # Read markdown file directly as text
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "source": str(md_file.name),
                    "source_type": "markdown",
                    "full_path": str(md_file)
                }
            )
            
            documents.append(doc)
            logger.info(f"Loaded {md_file.name} ({len(content)} characters)")
            
        except Exception as e:
            logger.error(f"Error loading {md_file}: {e}")
    
    return documents

def load_pdf_documents(pdf_dir: Path) -> List[Document]:
    """Load and process PDF documents"""
    documents = []
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    logger.info(f"Found {len(pdf_files)} PDF files")
    
    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            
            # Add metadata
            for i, doc in enumerate(docs):
                doc.metadata.update({
                    "source": str(pdf_file.name),
                    "source_type": "pdf",
                    "page": i + 1,
                    "full_path": str(pdf_file)
                })
            
            documents.extend(docs)
            logger.info(f"Loaded {len(docs)} pages from {pdf_file.name}")
            
        except Exception as e:
            logger.error(f"Error loading {pdf_file}: {e}")
    
    return documents

def load_csv_documents(csv_dir: Path) -> List[Document]:
    """Load and process CSV documents"""
    documents = []
    csv_files = list(csv_dir.glob("*.csv"))
    
    logger.info(f"Found {len(csv_files)} CSV files")
    
    for csv_file in csv_files:
        try:
            # Load CSV and convert rows to documents
            df = pd.read_csv(csv_file)
            
            for index, row in df.iterrows():
                # Convert row to text representation
                content = "\n".join([f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])])
                
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": str(csv_file.name),
                        "source_type": "csv",
                        "row_index": index,
                        "full_path": str(csv_file)
                    }
                )
                documents.append(doc)
            
            logger.info(f"Loaded {len(df)} rows from {csv_file.name}")
            
        except Exception as e:
            logger.error(f"Error loading {csv_file}: {e}")
    
    return documents

def calculate_documents_hash(documents: List[Document]) -> str:
    """Calculate a hash of all documents to detect changes"""
    content_hash = hashlib.md5()
    
    for doc in sorted(documents, key=lambda x: x.metadata.get('source', '')):
        # Include both content and metadata in hash
        doc_string = f"{doc.page_content}|{json.dumps(doc.metadata, sort_keys=True)}"
        content_hash.update(doc_string.encode('utf-8'))
    
    return content_hash.hexdigest()

def should_recreate_vector_store(documents: List[Document], persist_directory: str) -> bool:
    """Check if vector store needs to be recreated based on document changes"""
    hash_file = Path(persist_directory) / "documents_hash.txt"
    
    # Calculate current documents hash
    current_hash = calculate_documents_hash(documents)
    
    # Check if vector store exists and has valid hash
    if not os.path.exists(persist_directory) or not hash_file.exists():
        logger.info("Vector store doesn't exist or is missing hash - will create new one")
        return True
    
    try:
        with open(hash_file, 'r') as f:
            stored_hash = f.read().strip()
        
        if current_hash != stored_hash:
            logger.info("Documents have changed - will recreate vector store")
            return True
        else:
            logger.info("Documents unchanged - using existing vector store")
            return False
            
    except Exception as e:
        logger.warning(f"Error reading hash file: {e} - will recreate vector store")
        return True

def save_documents_hash(documents: List[Document], persist_directory: str):
    """Save the current documents hash for future comparisons"""
    hash_file = Path(persist_directory) / "documents_hash.txt"
    current_hash = calculate_documents_hash(documents)
    
    with open(hash_file, 'w') as f:
        f.write(current_hash)
    
    logger.info(f"Saved documents hash: {current_hash[:8]}...")

def estimate_token_count(text: str) -> int:
    """Rough estimation of token count (1 token ≈ 4 characters for text-embedding models)"""
    return len(text) // 4

def filter_documents_by_token_limit(documents: List[Document], max_tokens_per_batch: int = 250000) -> List[List[Document]]:
    """Split documents into batches that respect token limits"""
    batches = []
    current_batch = []
    current_tokens = 0
    
    for doc in documents:
        doc_tokens = estimate_token_count(doc.page_content)
        
        # If single document exceeds limit, split it further
        if doc_tokens > max_tokens_per_batch:
            logger.warning(f"Document {doc.metadata.get('source', 'Unknown')} has {doc_tokens} tokens, splitting further")
            
            # Split the large document into smaller pieces
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,  # smaller chunks for large documents
                chunk_overlap=50,
                length_function=len
            )
            sub_docs = text_splitter.split_documents([doc])
            
            # Add sub-documents to batches
            for sub_doc in sub_docs:
                sub_tokens = estimate_token_count(sub_doc.page_content)
                if current_tokens + sub_tokens > max_tokens_per_batch and current_batch:
                    batches.append(current_batch)
                    current_batch = [sub_doc]
                    current_tokens = sub_tokens
                else:
                    current_batch.append(sub_doc)
                    current_tokens += sub_tokens
        else:
            # Check if adding this document would exceed the limit
            if current_tokens + doc_tokens > max_tokens_per_batch and current_batch:
                batches.append(current_batch)
                current_batch = [doc]
                current_tokens = doc_tokens
            else:
                current_batch.append(doc)
                current_tokens += doc_tokens
    
    # Add the last batch if it has documents
    if current_batch:
        batches.append(current_batch)
    
    return batches

def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents into smaller chunks for better retrieval"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    split_docs = text_splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
    
    return split_docs

def create_vector_store(documents: List[Document], persist_directory: str, force_recreate: bool = False) -> Chroma:
    """Create and persist ChromaDB vector store with smart recreation
    
    Uses cosine similarity for optimal semantic search performance with text embeddings.
    Cosine similarity focuses on the direction (meaning) of vectors rather than magnitude,
    making it ideal for text-based similarity comparisons.
    """
    
    # Check if we need to recreate the vector store
    if not force_recreate and not should_recreate_vector_store(documents, persist_directory):
        # Load existing vector store
        try:
            embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",
                chunk_size=100,  # Match the chunk size used for creation
                max_retries=3,
                request_timeout=60
            )
            
            vector_store = Chroma(
                persist_directory=persist_directory,
                embedding_function=embeddings,
                collection_name="rag_documents",
                collection_metadata={"hnsw:space": "cosine"}  # Use cosine similarity for semantic search
            )
            
            logger.info(f"Loaded existing vector store from {persist_directory}")
            return vector_store
            
        except Exception as e:
            logger.warning(f"Error loading existing vector store: {e} - will recreate")
    
    # Initialize OpenAI embeddings with much smaller chunk size to avoid token limits
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
        chunk_size=100,  # Much smaller batch size to avoid token limits
        max_retries=3,   # Add retries for robustness
        request_timeout=60  # Add timeout
    )
    
    # Remove existing collection if it exists to start fresh
    if os.path.exists(persist_directory):
        shutil.rmtree(persist_directory)
        logger.info(f"Removed existing vector store at {persist_directory}")
    
    # Create storage directory
    os.makedirs(persist_directory, exist_ok=True)
    
    # Use smart batching based on token limits
    document_batches = filter_documents_by_token_limit(documents, max_tokens_per_batch=200000)
    
    vector_store = None
    successful_batches = 0
    total_batches = len(document_batches)
    
    logger.info(f"Split {len(documents)} documents into {total_batches} smart batches based on token limits")
    
    for batch_num, batch in enumerate(document_batches, 1):
        estimated_tokens = sum(estimate_token_count(doc.page_content) for doc in batch)
        logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} documents, ~{estimated_tokens:,} tokens)")
        
        try:
            if vector_store is None:
                # Create the vector store with first batch
                vector_store = Chroma.from_documents(
                    documents=batch,
                    embedding=embeddings,
                    persist_directory=persist_directory,
                    collection_name="rag_documents",
                    collection_metadata={"hnsw:space": "cosine"}  # Use cosine similarity for semantic search
                )
            else:
                # Add remaining documents to existing store
                vector_store.add_documents(batch)
            
            successful_batches += 1
            logger.info(f"✅ Successfully processed batch {batch_num}")
            
        except Exception as e:
            logger.error(f"❌ Error processing batch {batch_num}: {e}")
            
            # If it's a token limit error, try to split this batch further
            if "max_tokens_per_request" in str(e):
                logger.info(f"Token limit exceeded for batch {batch_num}, trying smaller sub-batches...")
                
                # Split the failed batch into even smaller pieces
                sub_batches = filter_documents_by_token_limit(batch, max_tokens_per_batch=100000)
                
                for sub_batch_num, sub_batch in enumerate(sub_batches, 1):
                    try:
                        sub_tokens = sum(estimate_token_count(doc.page_content) for doc in sub_batch)
                        logger.info(f"  Processing sub-batch {sub_batch_num}/{len(sub_batches)} (~{sub_tokens:,} tokens)")
                        
                        if vector_store is None:
                            vector_store = Chroma.from_documents(
                                documents=sub_batch,
                                embedding=embeddings,
                                persist_directory=persist_directory,
                                collection_name="rag_documents",
                                collection_metadata={"hnsw:space": "cosine"}  # Use cosine similarity for semantic search
                            )
                        else:
                            vector_store.add_documents(sub_batch)
                        
                        logger.info(f"  ✅ Sub-batch {sub_batch_num} successful")
                        
                    except Exception as sub_e:
                        logger.error(f"  ❌ Sub-batch {sub_batch_num} failed: {sub_e}")
                        continue
                
                successful_batches += 1  # Count the parent batch as successful if any sub-batch worked
            else:
                # Continue with next batch for other types of errors
                continue
    
    if vector_store is None:
        raise ValueError("Failed to create vector store - all batches failed")
    
    if successful_batches < total_batches:
        logger.warning(f"Only {successful_batches}/{total_batches} batches processed successfully")
    
    # Save the documents hash for future comparisons
    save_documents_hash(documents, persist_directory)
    
    logger.info(f"✅ Created vector store with {len(documents)} documents ({successful_batches}/{total_batches} batches)")
    logger.info(f"📁 Vector store persisted to: {persist_directory}")
    
    return vector_store

def main():
    """Main function to create vector storage"""
    import sys
    
    # Check for force recreate flag
    force_recreate = "--force" in sys.argv or "-f" in sys.argv
    
    if force_recreate:
        logger.info("🔄 Force recreation requested")
    
    try:
        # Load environment variables
        load_environment()
        
        # Set up paths
        base_dir = Path(__file__).parent
        markdown_dir = base_dir / "markdown"
        pdf_dir = base_dir / "pdf"
        csv_dir = base_dir / "csv"
        storage_dir = base_dir.parent / "rag_storage"
        
        # Create storage directory if it doesn't exist
        storage_dir.mkdir(exist_ok=True)
        
        # Load documents from all sources
        all_documents = []
        
        if markdown_dir.exists():
            all_documents.extend(load_markdown_documents(markdown_dir))
        
        if pdf_dir.exists():
            all_documents.extend(load_pdf_documents(pdf_dir))
        
        if csv_dir.exists():
            all_documents.extend(load_csv_documents(csv_dir))
        
        if not all_documents:
            logger.warning("No documents found to process")
            return
        
        logger.info(f"📚 Total documents loaded: {len(all_documents)}")
        
        # Split documents into chunks
        split_docs = split_documents(all_documents)
        
        # Create vector store (with smart recreation)
        vector_store = create_vector_store(split_docs, str(storage_dir), force_recreate=force_recreate)
        
        logger.info("🎉 Vector storage creation completed successfully!")
        
        # Test the vector store
        test_query = "What is this about?"
        results = vector_store.similarity_search(test_query, k=3)
        logger.info(f"🔍 Test search returned {len(results)} results")
        
        for i, result in enumerate(results):
            source = result.metadata.get('source', 'Unknown')
            content_preview = result.page_content[:100] + "..." if len(result.page_content) > 100 else result.page_content
            logger.info(f"  📄 Result {i+1}: {source} - {len(result.page_content)} chars")
            logger.info(f"     Preview: {content_preview}")
        
        # Print usage instructions
        print("\n" + "="*60)
        print("🚀 Vector Storage Ready!")
        print("="*60)
        print("✅ Your documents are now indexed and ready for RAG queries")
        print("📁 Storage location:", storage_dir)
        print(f"📊 Total chunks: {len(split_docs)}")
        print("\n💡 Usage:")
        print("   • Run chatbot: cd .. && uv run python template_runner.py")
        print("   • Force recreate: python create_vector_storage.py --force")
        print("   • Next time: Only recreates if documents change!")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ Error creating vector storage: {e}")
        print(f"\n💡 Troubleshooting:")
        print(f"   • Check your OPENAI_API_KEY in .env file")
        print(f"   • Ensure you have credits in your OpenAI account")
        print(f"   • Try running with --force flag")
        raise

if __name__ == "__main__":
    main()
    # to run this script with uv, use: `uv run python chatbot/rag_input_documents/create_vector_storage.py`