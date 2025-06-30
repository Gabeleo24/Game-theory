"""
Vector store implementation for RAG system using ChromaDB.
"""

import chromadb
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from sentence_transformers import SentenceTransformer
import os

from ..utils.config import Config


class VectorStore:
    """Vector store for storing and retrieving document embeddings."""
    
    def __init__(self):
        """Initialize the vector store."""
        self.config = Config()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.collection_name = self.config.get('rag_system.vector_store.collection_name', 'soccer_intelligence')
        self.embedding_model_name = 'all-MiniLM-L6-v2'  # Lightweight model
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            self.logger.info(f"Loaded embedding model: {self.embedding_model_name}")
        except Exception as e:
            self.logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        
        # Initialize ChromaDB
        try:
            self.client = chromadb.Client()
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Soccer intelligence documents"}
            )
            self.logger.info(f"Initialized ChromaDB collection: {self.collection_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of document dictionaries with 'id', 'content', 'type', 'metadata'
        """
        if not self.embedding_model or not self.collection:
            self.logger.error("Vector store not properly initialized")
            return
        
        self.logger.info(f"Adding {len(documents)} documents to vector store")
        
        try:
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            metadatas = []
            documents_content = []
            
            for doc in documents:
                # Generate embedding
                embedding = self.embedding_model.encode(doc['content'])
                
                ids.append(doc['id'])
                embeddings.append(embedding.tolist())
                documents_content.append(doc['content'])
                
                # Prepare metadata
                metadata = doc.get('metadata', {})
                metadata['type'] = doc.get('type', 'unknown')
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents_content,
                metadatas=metadatas
            )
            
            self.logger.info(f"Successfully added {len(documents)} documents")
            
        except Exception as e:
            self.logger.error(f"Error adding documents to vector store: {e}")
    
    def search(self, query: str, top_k: int = 5, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_type: Optional filter by document type
            
        Returns:
            List of search results with similarity scores
        """
        if not self.embedding_model or not self.collection:
            self.logger.error("Vector store not properly initialized")
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query)
            
            # Prepare where clause for filtering
            where_clause = None
            if filter_type:
                where_clause = {"type": filter_type}
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'type': results['metadatas'][0][i].get('type', 'unknown'),
                        'metadata': results['metadatas'][0][i]
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching vector store: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        if not self.collection:
            return {'error': 'Collection not initialized'}
        
        try:
            count = self.collection.count()
            return {
                'collection_name': self.collection_name,
                'document_count': count,
                'embedding_model': self.embedding_model_name
            }
        except Exception as e:
            return {'error': str(e)}
    
    def clear_collection(self) -> None:
        """Clear all documents from the collection."""
        if not self.collection:
            self.logger.error("Collection not initialized")
            return
        
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Soccer intelligence documents"}
            )
            self.logger.info("Collection cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing collection: {e}")
