import os
import pandas as pd
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import json
import chromadb


def initialize_embedding(device: str = 'mps', model_name: str = "intfloat/multilingual-e5-large") -> HuggingFaceEmbeddings:
    """
    Initialize the HuggingFace embedding model.
    
    Args:
        device (str, optional): The device to run the model on ('cpu', 'cuda', 'mps'). 
                              Defaults to 'mps'.
        model_name (str, optional): The name of the HuggingFace model to use. 
                                  Defaults to 'intfloat/multilingual-e5-large'.
    
    Returns:
        HuggingFaceEmbeddings: Initialized embedding model
    """
    model_kwargs = {'device': device}
    return HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, show_progress=True)


def load_news_data(file_path: str) -> pd.DataFrame:
    """
    Load and preprocess news data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file containing news data
    
    Returns:
        pd.DataFrame: Processed DataFrame with non-null news content
    """
    # Read JSON file as a list of records
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    df = df.dropna(subset=['news_content'])
    return df


def split_and_filter_documents(df: pd.DataFrame, chunk_size: int = 500, chunk_overlap: int = 50) -> list[Document]:
    """
    Split news content into chunks and create Document objects with metadata.
    
    Args:
        df (pd.DataFrame): DataFrame containing news data
        chunk_size (int, optional): Size of each text chunk. Defaults to 500.
        chunk_overlap (int, optional): Overlap between chunks. Defaults to 50.
    
    Returns:
        list[Document]: List of Document objects containing text chunks and metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\\n\\n", "\\n", "。", "，", "；", "！"]
    )

    documents = []
    for _, row in df.iterrows():
        content = row['news_content']
        if len(content.strip()) > 20:
            splits = splitter.split_text(content)
            cleaned = [s for s in splits if len(s.strip()) > 70]
            for i, split in enumerate(cleaned):
                documents.append(Document(
                    page_content=split,
                    metadata={
                        "news_id": f"{row['news_id']}",
                        "date": row['date'],
                        "news_title": row['news_title'],
                        "chunk_id": i
                    }
                ))
    return documents


def store_documents_in_chroma(docs: list[Document], 
                            embedding: HuggingFaceEmbeddings, 
                            persist_directory: str = "./backend/storage/chromadb", 
                            batch_size: int = 1000) -> None:
    """
    Store document chunks in ChromaDB with embeddings.
    
    Args:
        docs (list[Document]): List of Document objects to store
        embedding (HuggingFaceEmbeddings): Embedding model to use
        persist_directory (str, optional): Directory to persist the database. 
                                         Defaults to "./backend/storage/chromadb".
        batch_size (int, optional): Number of documents to process in each batch. 
                                  Defaults to 1000.
    """
    # Create directory if it doesn't exist
    os.makedirs(persist_directory, exist_ok=True)
    
    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=persist_directory)
    
    # Create or get collection
    vectordb = Chroma(
        client=client,
        embedding_function=embedding,
        collection_name="news_collection"
    )
    
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]
        vectordb.add_documents(batch)
        print(f"已處理 {i + len(batch)} 筆資料...")
    print("所有文件已成功存入 ChromaDB")


def process_news_files(directory: str, 
                      file_list: list[str], 
                      persist_directory: str = "./backend/storage/chromadb") -> None:
    """
    Process multiple news files and store them in ChromaDB.
    
    Args:
        directory (str): Directory containing the news files
        file_list (list[str]): List of file names to process
        persist_directory (str, optional): Directory to persist the database. 
                                         Defaults to "./backend/storage/chromadb".
    """
    # Create directory if it doesn't exist
    os.makedirs(persist_directory, exist_ok=True)
    
    # Initialize embedding model
    embedding = initialize_embedding()
    
    for file_name in file_list:
        file_path = os.path.join(directory, file_name)
        if os.path.exists(file_path):
            print(f"處理中：{file_name}")
            try:
                df = load_news_data(file_path)
                docs = split_and_filter_documents(df)
                store_documents_in_chroma(docs, embedding, persist_directory)
            except Exception as e:
                print(f"處理 {file_name} 發生錯誤：{e}")
        else:
            print(f"找不到 {file_name}，已跳過。")