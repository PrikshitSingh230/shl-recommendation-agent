import json

from groq import Groq

from services.prompts import (
    SYSTEM_PROMPT,
    OFF_TOPIC_PATTERNS
)

from services.response_parser import (
    validate_and_fix_schema
)

from services.retrieval import (
    hybrid_search
)


# groq loader

def load_groq_client(api_key):

    client = Groq(
        api_key=api_key
    )

    return client


# conversation query extraction

def get_user_context_query(messages):

    user_messages = []

    for msg in messages:

        if msg["role"] == "user":

            user_messages.append(
                msg["content"]
            )

    return " ".join(user_messages)


# catalog grounding

def build_catalog_context(retrieved_results):

    lines = []

    for i, item in enumerate(
        retrieved_results,
        start=1
    ):

        lines.append(
            f"""
Assessment {i}

Name: {item['name']}\n

URL (COPY EXACTLY): {item['url']}\n

Type: {item['test_type']}

Description: {item.get('description', '')}

Job Levels:
{', '.join(item.get('job_levels', []))}

Duration:
{item.get('duration_minutes')}

Remote Testing:
{item.get('remote_testing')}

Adaptive Testing:
{item.get('adaptive_testing')}
"""
        )

    return "\n\n".join(lines)


# main agent response

def generate_agent_response(

    messages,

    groq_client,

    embedding_model,

    index,

    bm25,

    catalog
):

    query = get_user_context_query(
        messages
    )

    query_lower = query.lower()

    # off-topic guard

    is_off_topic = any(

        keyword in query_lower

        for keyword in OFF_TOPIC_PATTERNS
    )

    if is_off_topic:

        return {

            "reply": (
                "I can only help with SHL "
                "assessment recommendations."
            ),

            "recommendations": [],

            "end_of_conversation": False
        }

    # empty query guard

    if not query:

        return {

            "reply": (
                "I didn't receive a message."
            ),

            "recommendations": [],

            "end_of_conversation": False
        }

    try:

        # retrieval

        retrieved_results = hybrid_search(

            query=query,

            model=embedding_model,

            index=index,

            bm25=bm25,

            catalog=catalog,

            k=6
        )

        # grounding

        catalog_context = build_catalog_context(
            retrieved_results
        )

        full_system = (

            SYSTEM_PROMPT

            + f"\n\nCATALOG CONTEXT:\n"

            + catalog_context
        )

        # llm call

        response = groq_client.chat.completions.create(

            model="llama-3.1-8b-instant",

            temperature=0.1,

            max_tokens=512,

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": full_system
                },

                *messages
            ]
        )

        content = (
            response
            .choices[0]
            .message.content
        )

        parsed = json.loads(content)

        return validate_and_fix_schema(
            parsed,
            catalog
        )

    except json.JSONDecodeError as e:

        print(f"JSON ERROR: {e}")

        return {

            "reply": (
                "I encountered an issue "
                "processing your request."
            ),

            "recommendations": [],

            "end_of_conversation": False
        }

    except Exception as e:

        print(
            f"ERROR: {type(e).__name__}: {e}"
        )

        return {

            "reply": (
                "I'm temporarily unavailable."
            ),

            "recommendations": [],

            "end_of_conversation": False
        }