def validate_and_fix_schema(parsed: dict, catalog=None) -> dict:

    # Build URL lookup from catalog if provided
    catalog_url_lookup = {}
    if catalog:
        catalog_url_lookup = {
            item["name"].lower(): item["url"]
            for item in catalog
        }

    recommendations = parsed.get("recommendations") or []
    if not isinstance(recommendations, list):
        recommendations = []

    cleaned_recommendations = []
    seen_urls = set()

    for rec in recommendations:
        if not isinstance(rec, dict):
            continue

        name      = rec.get("name")
        url       = rec.get("url")
        test_type = rec.get("test_type")

        if not name or not url:
            continue

        # Fix hallucinated URLs using catalog — exact match first, then fuzzy
        if catalog:
            correct_url = catalog_url_lookup.get(name.lower())
            if correct_url:
                url = correct_url
            else:
                for cat_name, cat_url in catalog_url_lookup.items():
                    if name.lower() in cat_name or cat_name in name.lower():
                        url = cat_url
                        break

        # Drop non-SHL URLs
        if not url.startswith("https://www.shl.com/"):
            continue

        # Deduplicate
        if url in seen_urls:
            continue
        seen_urls.add(url)

        cleaned_recommendations.append({
            "name":      name,
            "url":       url,
            "test_type": test_type or "Unknown"
        })

    return {
        "reply":               parsed.get("reply", "I'm sorry, something went wrong."),
        "recommendations":     cleaned_recommendations[:10],
        "end_of_conversation": bool(parsed.get("end_of_conversation", False))
    }