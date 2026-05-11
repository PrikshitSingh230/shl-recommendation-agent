# test type mapping
import json
import re
import unicodedata

test_type_keywords = {
    "A": [
        "ability", "aptitude", "cognitive",
        "numerical", "verbal", "reasoning",
        "spatial", "mechanical"
    ],

    "B": [
        "biodata",
        "situational judgment",
        "sjt"
    ],

    "C": [
        "competency",
        "competencies",
        "360",
        "development"
    ],

    "D": [
        "assessment exercises",
        "simulation",
        "role play",
        "in-tray"
    ],

    "E": [
        "assessment exercises"
    ],

    "K": [
        "knowledge",
        "skills",
        "technical"
    ],

    "P": [
        "personality",
        "behavior",
        "behaviour",
        "motivation",
        "values"
    ],
}


# helpers

def get_test_type(keys: list[str]) -> str:

    keys_text = " ".join(keys).lower()

    for code, keywords in test_type_keywords.items():

        if any(kw in keys_text for kw in keywords):
            return code

    return "Other"


def clean_text(text: str) -> str:

    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def duration_to_minutes(duration_str: str):

    if not duration_str:
        return None

    match = re.search(r"\d+", str(duration_str))

    return int(match.group()) if match else None


def parse_bool(val):

    if isinstance(val, bool):
        return val

    if isinstance(val, str):
        return val.strip().lower() in (
            "yes",
            "true",
            "1"
        )

    return None


# catalog loader

def load_and_process_catalog(filepath):

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed_catalog = []

    for item in data:

        name        = item.get("name", "").strip()
        description = item.get("description", "").strip()
        url         = item.get("link", "")
        raw_keys    = item.get("keys", [])

        job_levels  = item.get("job_levels", [])
        languages   = item.get("languages", [])

        duration    = item.get("duration", "")
        remote      = item.get("remote", "")
        adaptive    = item.get("adaptive", "")

        entity_id   = str(item.get("entity_id", ""))
        status      = item.get("status", "")

        test_type = get_test_type(raw_keys)

        # embedding text

        parts = [name]

        if description:
            parts.append(description)

        if raw_keys:
            parts.append(
                "Categories: " + ", ".join(raw_keys)
            )

        if job_levels:
            parts.append(
                "Job levels: " + ", ".join(job_levels)
            )

        if languages:
            parts.append(
                "Languages: " + ", ".join(languages)
            )

        if duration:
            parts.append(
                f"Duration: {duration}"
            )

        if remote:
            parts.append(
                f"Remote testing: {remote}"
            )

        if adaptive:
            parts.append(
                f"Adaptive testing: {adaptive}"
            )

        embedding_text = clean_text(
            " . ".join(parts)
        )

        # bm25 tokens

        bm25_tokens = clean_text(
            f"""
            {name}
            {description}
            {' '.join(raw_keys)}
            {' '.join(job_levels)}
            {' '.join(languages)}
            """
        ).split()

        # structured record

        processed_catalog.append({

            "embedding_text": embedding_text,
            "bm25_tokens": bm25_tokens,

            "entity_id": entity_id,
            "name": name,
            "description": description,
            "url": url,

            "test_type": test_type,

            "job_levels": job_levels,
            "languages": languages,

            "duration_minutes": duration_to_minutes(duration),

            "remote_testing": parse_bool(remote),

            "adaptive_testing": parse_bool(adaptive),

            "status": status,
        })

    print(f"Loaded {len(processed_catalog)} catalog items")

    return processed_catalog