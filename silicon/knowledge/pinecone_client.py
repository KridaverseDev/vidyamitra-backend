import os
import time
from typing import Optional

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_community.document_loaders.base import BaseLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
pc = Pinecone(api_key=PINECONE_API_KEY)


def get_embeddings(user=None, force_openai: bool = True):
    """
    Get OpenAI embeddings instance only.
    
    Args:
        user: Authenticated user (optional) - for user-specific API keys
        force_openai: If True, only use OpenAI (default: True)
    
    Returns:
        OpenAIEmbeddings instance
    
    Raises:
        ValueError: If no OpenAI API key is found
    """
    from silicon.util.api_key_helper import get_api_key_for_provider
    
    # Check user-specific OpenAI key first
    openai_key = get_api_key_for_provider(user, "openai")
    if not openai_key:
        # Fallback to env var
        openai_key = os.environ.get("OPENAI_API_KEY")
    
    if not openai_key:
        raise ValueError(
            "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
            "or add a user API key via POST /v1/user/api-keys/ with provider='openai'"
        )
    
    return OpenAIEmbeddings(openai_api_key=openai_key)


class PineconeClient:
    def __init__(self, user=None, force_openai: bool = True) -> None:
        """
        Initialize PineconeClient with OpenAI embeddings only.
        
        Args:
            user: Authenticated user (optional) - for user-specific API keys
            force_openai: If True, only use OpenAI embeddings (default: True)
        """
        self.user = user
        # Always use OpenAI embeddings
        self.embeddings = get_embeddings(user, force_openai=True)
        self.index = self._connect_pinecone()

    def _connect_pinecone(self):
        index_name = PINECONE_INDEX_NAME
        OPENAI_DIMENSION = 1536  # OpenAI embeddings dimension

        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

        if index_name in existing_indexes:
            # Index exists - check its dimension
            index_info = pc.describe_index(index_name)
            existing_dimension = index_info.dimension
            
            if existing_dimension != OPENAI_DIMENSION:
                # Dimension mismatch - need to delete and recreate
                print(f"WARNING: Existing index '{index_name}' has dimension {existing_dimension}, "
                      f"but OpenAI embeddings require {OPENAI_DIMENSION}.")
                print(f"Deleting old index and creating new one with dimension {OPENAI_DIMENSION}...")
                
                # Delete the old index
                pc.delete_index(index_name)
                
                # Wait for deletion to complete
                while index_name in [idx["name"] for idx in pc.list_indexes()]:
                    time.sleep(1)
                
                # Create new index with correct dimension
                pc.create_index(
                    name=index_name,
                    dimension=OPENAI_DIMENSION,
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1"),
                )
                while not pc.describe_index(index_name).status["ready"]:
                    time.sleep(1)
                
                print(f"Successfully created new index '{index_name}' with dimension {OPENAI_DIMENSION}")
        else:
            # Index doesn't exist - create it with OpenAI dimension
            pc.create_index(
                name=index_name,
                dimension=OPENAI_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
            while not pc.describe_index(index_name).status["ready"]:
                time.sleep(1)

        self.index = pc.Index(index_name)
        return self.index

    def save(self, filename, loader: BaseLoader):
        documents = loader.load()
        docs = text_splitter.split_documents(documents)
        docsearch = PineconeVectorStore.from_documents(
            docs, self.embeddings, index_name=PINECONE_INDEX_NAME, namespace=filename
        )

    def query(self, namespace: str, query: str):
        """
        Query the vector store using multi-query retrieval with OpenAI.
        Uses the same OpenAI API key as embeddings for consistency.
        """
        from silicon.util.api_key_helper import get_api_key_for_provider
        
        vectorstore = PineconeVectorStore(
            embedding=self.embeddings, namespace=namespace, index_name=PINECONE_INDEX_NAME
        )
        
        # Get OpenAI API key (same as embeddings)
        openai_key = None
        if hasattr(self, 'user') and self.user:
            openai_key = get_api_key_for_provider(self.user, "openai")
        if not openai_key:
            openai_key = os.environ.get("OPENAI_API_KEY")
        
        if not openai_key:
            raise ValueError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable "
                "or add a user API key via POST /v1/user/api-keys/ with provider='openai'"
            )
        
        # Use OpenAI instead of Gemini for consistency
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            openai_api_key=openai_key,
        )
        retriever = MultiQueryRetriever.from_llm(
            retriever=vectorstore.as_retriever(), llm=llm
        )
        return retriever.invoke(query)

    def search(self, namespace: str, query: str):
        vectorstore = PineconeVectorStore(
            embedding=self.embeddings, namespace=namespace, index_name=PINECONE_INDEX_NAME
        )
        result = vectorstore.similarity_search(query)
        result = [self._get_response(r) for r in result]

        return result

    def get_namespaces(self):
        index = pc.Index(PINECONE_INDEX_NAME)
        result = index.describe_index_stats()
        return {"namepaces": result.to_dict()["namespaces"]}

    def _get_response(self, result):
        return {
            "page_content": result.page_content,
            "metadata": result.metadata,
        }

    def delete_namespace(self, namespace: str):
        index_name = PINECONE_INDEX_NAME
        index = pc.Index(index_name)

        # Deleting the namespace
        self.index.delete(namespace=namespace, delete_all=True)
        # Optionally, you can wait and verify if the namespace is deleted or handle errors
