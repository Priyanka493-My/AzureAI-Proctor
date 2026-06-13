import os
import faiss
import numpy as np
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

class LocalSyllabusRAG:
    def __init__(self):
        print("Loading local embedding model...")
        self.emdedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_chunks = []

        # Paths
        self.pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ai900_syllabus.pdf"))
        self.index_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../faiss_db"))
        self.index_path = os.path.join(self.index_dir, "faiss_index.bin")
        self.chunks_path = os.path.join(self.index_dir, "text_chunks.npy")

    def extract_text_pdf(self)-> str:
        reader = PdfReader(self.pdf_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text: full_text += text +"\n"
        return full_text

    def chunk_text(self,text:str,chunk_size:int = 500,overlap:int = 50)->list:
        words = text.split()
        chunks = []
        for i in range(0,len(words),chunk_size - overlap):
            chunks.append(" ".join(words[i:i+chunk_size]))
        return chunks


    def initialize_vector_store(self):
        os.makedirs(self.index_dir, exist_ok=True)
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            self.text_chunks = list(np.load(self.chunks_path,allow_pickle=True))
        else:
            raw_text = self.extract_text_pdf()
            self.text_chunks = self.chunk_text(raw_text)
        embeddings = self.emdedding_model.encode(self.text_chunks)
        embeddings_array = np.array(embeddings).astype('float32')
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        faiss.normalize_L2(embeddings_array)
        self.index.add(embeddings_array)
        faiss.write_index(self.index,self.index_path)
        np.save(self.chunks_path,np.array(self.text_chunks,dtype = object))

    def retrieve_context(self,query:str,top_k :int = 3)->str:
        query_vector = self.emdedding_model.encode([query]).astype('float32')
        faiss.normalize_L2(query_vector)
        similarities,indices = self.index.search(query_vector,top_k)
        match_ids = indices[0]
        retrieved_segments = [self.text_chunks[idx]for idx in match_ids if idx!=-1]
        return "\n---\n".join(retrieved_segments)
if __name__ == '__main__':

    # Initialize the RAG system
    rag = LocalSyllabusRAG()

    # Process the PDF or load the existing index from disk
    rag.initialize_vector_store()

    # Run a test search query to verify retrieval is working
    test_query = "What are the core requirements and tools for Microsoft Foundry applications?"
    print(f"\n🔍 Testing RAG search for: '{test_query}'")

    context = rag.retrieve_context(test_query,top_k = 2)

    print("\n📚 [RETRIEVED SYLLABUS CONTEXT]:")
    print(context)
