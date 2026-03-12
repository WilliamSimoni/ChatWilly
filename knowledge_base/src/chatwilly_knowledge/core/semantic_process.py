import json
import re

from chatwilly_knowledge.core.categories import categories
from chatwilly_knowledge.core.response import ExtractionResponse
from chatwilly_knowledge.prompt.processor_prompt import (
    EXTRACTION_PROMPT,
    SUMMARY_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
)
from chatwilly_knowledge.settings import knowledge_settings
from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError


def extract_json_from_tags(content: str) -> dict:
    """
    Extracts JSON content located between <out> and </out> tags.
    """
    pattern = r"<out>(.*?)</out>"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON within tags: {e}")
    else:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise ValueError("No <out> tags found and content is not valid JSON.")


def generate_summary(text: str, llm) -> str:
    """Generates the global document summary."""
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", SUMMARY_SYSTEM_PROMPT),
            ("human", SUMMARY_PROMPT),
        ]
    )
    chain = prompt_template | llm

    response = chain.invoke(
        {"text": text[: knowledge_settings.max_document_characters]}
    )
    return response.content.strip()


def semantic_process(text: str, llm) -> dict:
    """
    Returns a dictionary containing the summary and the chunks.
    """
    print("Generating document summary")
    document_summary = generate_summary(text, llm)

    categories_definitions_str = ""
    for category in categories:
        categories_definitions_str += (
            f"\n- **{category.name}**: {category.description}\n"
        )

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", EXTRACTION_PROMPT),
        ]
    )

    chain = prompt_template | llm

    try:
        response_message = chain.invoke(
            {
                "categories_definitions_str": categories_definitions_str,
                "document_summary": document_summary,
                "text": text[: knowledge_settings.max_document_characters],
            }
        )

        raw_content = response_message.content
        json_data = extract_json_from_tags(raw_content)

        validated_response = ExtractionResponse(**json_data)
        chunks_dump = [chunk.model_dump() for chunk in validated_response.chunks]

        return {"document_summary": document_summary, "chunks": chunks_dump}

    except ValidationError as ve:
        print(f"Pydantic Validation Error: {ve}")
        return {}
    except Exception as e:
        print(f"Error processing text: {e}")
        return {}
