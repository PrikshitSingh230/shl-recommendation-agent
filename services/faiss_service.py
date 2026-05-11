import faiss
import os
import numpy as np


# faiss loader

def load_or_create_faiss_index(
    embeddings,
    faiss_path="data/faiss.index"
):

    dimension = embeddings.shape[1]

    if os.path.exists(faiss_path):

        print("loading faiss index from disk...")

        index = faiss.read_index(faiss_path)

    else:

        print("creating faiss index...")

        index = faiss.IndexFlatIP(dimension)

        index.add(
            np.array(embeddings).astype("float32")
        )

        faiss.write_index(index, faiss_path)

        print(f"faiss index saved to {faiss_path}")

    print("total vectors in index:", index.ntotal)

    return index


# faiss search

def search_faiss(
    query,
    model,
    index,
    catalog,
    k=10
):

    query_vector = model.encode(

        [query],

        normalize_embeddings=True,

        convert_to_numpy=True
    )

    scores, indices = index.search(

        np.array(query_vector).astype("float32"),

        k
    )

    results = []

    for score, idx in zip(
        scores[0],
        indices[0]
    ):

        item = catalog[idx]

        results.append({

            "name": item["name"],

            "url": item["url"],

            "test_type": item["test_type"],

            "score": float(score),

            "idx": int(idx)
        })

    return results