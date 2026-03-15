import logging

from langchain.tools import tool

from chatwilly_backend.vector_db.retriever import vector_search

logger = logging.getLogger(__name__)


@tool
async def search_work_experience_and_projects(query: str) -> str:
    """
    Use this tool to search for specific projects, work experiences, career history,
    roles covered, or quantifiable achievements (e.g. "What did you build at the startup?",
    "Tell me about a time you optimized a database").

    Args:
        query: Specific search terms (e.g., "startup architecture", "system optimization").
    """
    logger.info(
        "Tool 'search_work_experience_and_projects' invoked with query: '%s'", query
    )
    result = await vector_search(
        query, category="work_experience_and_projects", limit=5
    )
    logger.debug(
        "Successfully retrieved work experience results for query: '%s'", query
    )
    return result


@tool
async def search_technical_and_hard_skills(query: str) -> str:
    """
    Use this tool to verify if I know specific programming languages, frameworks,
    or tools, and how I used them (e.g. "Do you know Python?", "Experience with React?").

    Args:
        query: Specific technology name (e.g., "Python", "Docker", "Kubernetes").
    """
    logger.info(
        "Tool 'search_technical_and_hard_skills' invoked with query: '%s'", query
    )
    result = await vector_search(query, category="technical_and_hard_skills", limit=5)
    logger.debug(
        "Successfully retrieved technical skill results for query: '%s'", query
    )
    return result


@tool
async def search_soft_skills_and_behavioral(query: str) -> str:
    """
    Use this tool to search for behavioral anecdotes, soft skills, failures,
    teamwork, leadership, or how I handled difficult situations.

    Args:
        query: Behavioral trait or situation (e.g., "failure", "leadership", "conflict").
    """
    logger.info(
        "Tool 'search_soft_skills_and_behavioral' invoked with query: '%s'", query
    )
    result = await vector_search(query, category="soft_skills_and_behavioral", limit=5)
    logger.debug("Successfully retrieved behavioral results for query: '%s'", query)
    return result


@tool
async def search_education_logistics_and_goals(query: str) -> str:
    """
    Use this tool to search for factual data like education (degrees, university),
    notice period, current location, willingness to relocate, or future goals.

    Args:
        query: Factual inquiry (e.g., "university degree", "notice period", "location").
    """
    logger.info(
        "Tool 'search_education_logistics_and_goals' invoked with query: '%s'", query
    )
    result = await vector_search(
        query, category="education_logistics_and_goals", limit=5
    )
    logger.debug(
        "Successfully retrieved education/logistics results for query: '%s'", query
    )
    return result
