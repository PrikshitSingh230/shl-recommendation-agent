from rank_bm25 import BM25Okapi
import numpy as np

from services.preprocessing import clean_text


# bm25 builder

def build_bm25(catalog):

    bm25_corpus = [

        item["bm25_tokens"]

        for item in catalog
    ]

    bm25 = BM25Okapi(
        bm25_corpus
    )

    print("bm25 index built successfully")

    print(
        "total documents indexed:",
        len(bm25_corpus)
    )

    return bm25


# bm25 search

def search_bm25(
    query,
    bm25,
    catalog,
    k=10
):

    query_tokens = clean_text(
        query
    ).split()

    scores = bm25.get_scores(
        query_tokens
    )

    top_indices = np.argsort(scores)[::-1][:k]

    results = []

    for idx in top_indices:

        if scores[idx] > 0:

            item = catalog[idx]

            results.append({

                **item,

                "score": float(scores[idx]),

                "idx": int(idx)
            })

    return results