# 🚀 Imports
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import normalize

# 🚀 1. Load Fine-Tuned Model
model = SentenceTransformer('fine_tuned_patent_model')

# 🚀 2. Load Pre-computed Fine-Tuned Embeddings
doc_embeddings = np.load('fine_tuned_embeddings.npy')  # <<< Load embeddings from file here ✅

# 🚀 3. Normalize Embeddings
doc_embeddings = normalize(doc_embeddings)

# 🚀 4. Load Abstract Titles
import json
with open('patent_search_results.json', 'r', encoding='utf-8') as f:
    patent_data = json.load(f)

titles = [entry['title'] for entry in patent_data]

# 🚀 5. Take a User Query
query = input("\n🔎 Enter your search query: ")

query_embedding = model.encode(query)

# 🚀 6. Normalize Query Embedding
query_embedding = query_embedding / np.linalg.norm(query_embedding)

# 🚀 7. Calculate Dot Product
similarities = np.dot(doc_embeddings, query_embedding)

# 🚀 8. Top-K Retrieval
top_k = 5
top_indices = np.argsort(similarities)[::-1][:top_k]

# 🚀 9. Show Top Results
print(f"\n🎯 Top-{top_k} Results for Query: '{query}'\n")
for idx in top_indices:
    print(f"Title: {titles[idx]}")
    print(f"Similarity Score: {round(similarities[idx], 3)}\n")
