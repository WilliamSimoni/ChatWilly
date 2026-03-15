from .tools import (
    search_education_logistics_and_goals,
    search_soft_skills_and_behavioral,
    search_technical_and_hard_skills,
    search_work_experience_and_projects,
)

ALL_TOOLS = [
    search_work_experience_and_projects,
    search_education_logistics_and_goals,
    search_soft_skills_and_behavioral,
    search_technical_and_hard_skills,
]

__all__ = ["ALL_TOOLS"]
