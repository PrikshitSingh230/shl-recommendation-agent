from services.faiss_service import (
    search_faiss
)

from services.bm25_service import (
    search_bm25
)


# score normalization

def normalize_scores(results):

    if not results:
        return results

    scores = [

        r["score"]

        for r in results
    ]

    mn = min(scores)
    mx = max(scores)

    if mx == mn:

        return [

            {
                **r,
                "score": 1.0
            }

            for r in results
        ]

    normalized = []

    for r in results:

        normalized_score = (

            r["score"] - mn

        ) / (mx - mn)

        normalized.append({

            **r,

            "score": normalized_score
        })

    return normalized


# hybrid retrieval

def hybrid_search(

    query,

    model,

    index,

    bm25,

    catalog,

    k=10,

    faiss_weight=0.6,

    bm25_weight=0.4
):

    # faiss retrieval

    faiss_results = search_faiss(

        query=query,

        model=model,

        index=index,

        catalog=catalog,

        k=20
    )

    # bm25 retrieval

    bm25_results = search_bm25(

        query=query,

        bm25=bm25,

        catalog=catalog,

        k=20
    )

    # normalize

    faiss_results = normalize_scores(
        faiss_results
    )

    bm25_results = normalize_scores(
        bm25_results
    )

    # weighted merge

    combined_scores = {}

    combined_items = {}

    # faiss scores

    for result in faiss_results:

        idx = result["idx"]

        combined_scores[idx] = (

            combined_scores.get(idx, 0)

            + faiss_weight * result["score"]
        )

        combined_items[idx] = result

    # bm25 scores

    for result in bm25_results:

        idx = result["idx"]

        combined_scores[idx] = (

            combined_scores.get(idx, 0)

            + bm25_weight * result["score"]
        )

        combined_items[idx] = result

    # ranking

    ranked = sorted(

        combined_scores.items(),

        key=lambda x: x[1],

        reverse=True
    )

    # final output

    final_results = []

    for idx, score in ranked[:k]:

        item = combined_items[idx]

        final_results.append({

            **item,

            "hybrid_score": round(score, 4)
        })

    return final_results