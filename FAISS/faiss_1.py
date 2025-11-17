import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


# Load entries from JSON file
with open('patent_search_results_aa.json', 'r', encoding='utf-8') as f:
    entries = json.load(f)

# Get all abstracts
abstracts = [entry["abstract"] for entry in entries]

# Encode abstracts to normalized vectors
abstract_embeddings = model.encode(abstracts, convert_to_numpy=True, normalize_embeddings=True)

# Build FAISS index for cosine similarity (using inner product on normalized vectors)
dimension = abstract_embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)
index.add(abstract_embeddings)

# Multiple enriched query variations
queries = [
  "How AI is used in smart beekeeping systems powered by solar energy",
  "Solar-powered IoT devices for real-time hive monitoring in apiculture",
  "AI algorithms for detecting bee colony health and behavior patterns",
  "Sustainable beekeeping using renewable energy and machine learning",
  "Energy-efficient smart hive systems with predictive analytics for beekeeping"
]

# Encode and average the query embeddings
query_embeddings = model.encode(queries, convert_to_numpy=True, normalize_embeddings=True)
query_embedding = np.mean(query_embeddings, axis=0).reshape(1, -1)

# Search top-K similar entries
top_k = 15  # Limit to top 15 for stricter filtering
distances, indices = index.search(query_embedding, top_k)

# Define a similarity threshold
threshold = 0.5  # Stricter filtering for relevance

# Optional keyword-based beekeeping filter
beekeeping_keywords =["solar", "powered" ,"ai", "beekeeping" ,"system"]

def is_beekeeping_related(text):
    return any(word in text.lower() for word in beekeeping_keywords)

# Collect relevant entries
results = []
for i, (score, idx) in enumerate(zip(distances[0], indices[0])):
    entry = entries[idx]
    abstract_text = entry["abstract"]
    if score >= threshold and is_beekeeping_related(abstract_text) :
        results.append({
            "Title": entry["title"],
            "Application Number": entry["application_number"],
            "Abstract": abstract_text,
            "Similarity": round(float(score), 3)
        })

# Save results to a new JSON file
json_filename = "patent_search_results_relevant_beekeeping.json"
with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"Filtered beekeeping-relevant results saved to {json_filename}")
