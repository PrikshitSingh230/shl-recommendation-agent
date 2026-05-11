from sentence_transformers import SentenceTransformer
import numpy as np
import os


def load_embedding_model():

    model = SentenceTransformer(
        "BAAI/bge-small-en-v1.5"
    )

    return model


def load_or_generate_embeddings(
    processed_catalog,
    model,
    embedding_path="data/embeddings.npy"
):

    embedding_texts = [

        item["embedding_text"]

        for item in processed_catalog
    ]

    if os.path.exists(embedding_path):

        print("loading embeddings...")

        embeddings = np.load(
            embedding_path
        )

    else:

        print("generating embeddings...")

        embeddings = model.encode(

            embedding_texts,

            convert_to_numpy=True,

            show_progress_bar=True,

            batch_size=64,

            normalize_embeddings=True
        )

        np.save(
            embedding_path,
            embeddings
        )

        print(
            f"saved embeddings to "
            f"{embedding_path}"
        )

    print(
        "embedding shape:",
        embeddings.shape
    )

    return embeddings