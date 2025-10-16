from openai import OpenAI
import os
from typing import List, Dict, Any, Tuple
from embedding_service import generate_embedding, pinecone_index

# Initialize OpenAI
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def search_similar_documents(
    query: str,
    user_id: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for similar document chunks based on query
    
    Args:
        query: User's search query
        user_id: User ID for namespace isolation
        top_k: Number of top results to return
    
    Returns:
        List of similar document chunks with metadata
    """
    if not pinecone_index:
        raise Exception("Pinecone index not initialized")
    
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(query)
        
        # Search in user-specific namespace
        namespace = f"user_{user_id}"
        
        # Query Pinecone
        search_results = pinecone_index.query(
            vector=query_embedding,
            namespace=namespace,
            top_k=top_k,
            include_metadata=True,
            include_values=False  # We don't need the actual vectors back
        )
        
        # Format results
        results = []
        for match in search_results.matches:
            result = {
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata,
                "text": match.metadata.get("text", ""),
                "doc_name": match.metadata.get("doc_name", ""),
                "doc_id": match.metadata.get("doc_id", ""),
                "chunk_id": match.metadata.get("chunk_id", 0)
            }
            results.append(result)
        
        return results
        
    except Exception as e:
        print(f"Error searching documents: {e}")
        raise

def generate_response_with_context(
    query: str,
    context_chunks: List[Dict[str, Any]],
    max_context_length: int = 4000
) -> str:
    """
    Generate AI response using retrieved context
    
    Args:
        query: User's query
        context_chunks: Retrieved document chunks
        max_context_length: Maximum length of context to include
    
    Returns:
        AI-generated response
    """
    if not context_chunks:
        return "I couldn't find any relevant information in your documents to answer that question."
    
    # Build context from chunks
    context_parts = []
    current_length = 0
    
    for chunk in context_chunks:
        text = chunk.get("text", "")
        doc_name = chunk.get("doc_name", "Unknown Document")
        
        # Add document name prefix for citation
        chunk_text = f"[From {doc_name}]: {text}"
        
        # Check if adding this chunk would exceed max length
        if current_length + len(chunk_text) > max_context_length:
            break
        
        context_parts.append(chunk_text)
        current_length += len(chunk_text)
    
    context = "\n\n".join(context_parts)
    
    # Build the prompt
    system_prompt = """You are a helpful assistant that answers questions based on provided document context. 
    
    Instructions:
    1. Answer the question using ONLY the information provided in the context
    2. If the context doesn't contain enough information, say so clearly
    3. Be concise and accurate
    4. When possible, mention which document(s) you're referencing
    5. Do not make up information not present in the context"""
    
    user_prompt = f"""Context from documents:
{context}

Question: {query}

Please provide a clear answer based on the context above."""
    
    try:
        # Generate response using OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error generating response: {e}")
        raise

def extract_source_citations(search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract unique source documents with relevance scores
    
    Args:
        search_results: Results from vector search
    
    Returns:
        List of unique sources with highest relevance scores
    """
    sources = {}
    
    for result in search_results:
        doc_name = result.get("doc_name", "Unknown Document")
        score = result.get("score", 0.0)
        doc_id = result.get("doc_id", "")
        
        # Keep the highest score for each document
        if doc_name not in sources or sources[doc_name]["relevance_score"] < score:
            sources[doc_name] = {
                "doc_name": doc_name,
                "doc_id": doc_id,
                "relevance_score": round(score, 3)
            }
    
    # Sort by relevance score (highest first)
    sorted_sources = sorted(
        sources.values(),
        key=lambda x: x["relevance_score"],
        reverse=True
    )
    
    return sorted_sources

def search_and_generate_response(query: str, user_id: str) -> Dict[str, Any]:
    """
    Complete search and response generation pipeline
    
    Args:
        query: User's search query
        user_id: User ID for namespace isolation
    
    Returns:
        Dictionary containing response and sources
    """
    try:
        # Step 1: Search for similar documents
        search_results = search_similar_documents(query, user_id, top_k=5)
        
        if not search_results:
            return {
                "response": "I couldn't find any relevant information in your documents to answer that question. Please make sure you have uploaded documents and they have been processed successfully.",
                "sources": []
            }
        
        # Step 2: Generate response with context
        response = generate_response_with_context(query, search_results)
        
        # Step 3: Extract source citations
        sources = extract_source_citations(search_results)
        
        return {
            "response": response,
            "sources": sources
        }
        
    except Exception as e:
        print(f"Error in search and response generation: {e}")
        return {
            "response": "I'm sorry, I encountered an error while processing your question. Please try again later.",
            "sources": []
        }

def get_document_statistics(user_id: str) -> Dict[str, Any]:
    """
    Get statistics about user's documents in Pinecone
    
    Args:
        user_id: User ID
    
    Returns:
        Dictionary containing document statistics
    """
    if not pinecone_index:
        return {"error": "Pinecone index not initialized"}
    
    try:
        namespace = f"user_{user_id}"
        
        # Get index stats for the user's namespace
        stats = pinecone_index.describe_index_stats()
        namespace_stats = stats.namespaces.get(namespace, {})
        
        return {
            "total_vectors": namespace_stats.get("vector_count", 0),
            "namespace": namespace
        }
        
    except Exception as e:
        print(f"Error getting document statistics: {e}")
        return {"error": str(e)}