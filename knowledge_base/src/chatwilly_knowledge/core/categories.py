from enum import Enum
from typing import List

from pydantic import BaseModel


class Category(BaseModel):
    name: str
    description: str


categories: List[Category] = [
    Category(
        name="work_experience_and_projects",
        description=(
            "Deconstruct professional experiences into separate, self-contained narrative chunks. "
            "Create distinct chunks for a project's goal, the candidate's specific role, and a key "
            'quantifiable achievement (e.g., "Increased performance by 20%"). Do NOT create one '
            "giant block of text per job."
        ),
    ),
    Category(
        name="technical_and_hard_skills",
        description=(
            "Create 'skill-claim' chunks. For each technology found, extract phrase describing "
            "*how it was used*. It is expected and desired that this will create overlaps with "
            "'work_experience_and_projects'. Example: Instead of [\"Python\"], extract "
            '["Python with the Django framework for backend development"].'
        ),
    ),
    Category(
        name="soft_skills_and_behavioral",
        description=(
            "Extract complete anecdotes that illustrate a specific behavioral trait, not just single "
            "adjectives. If possible, structure the anecdote like a STAR method answer (Situation, Task, "
            'Action, Result). Example: Instead of ["Leadership"], extract ["Mentored a junior dev to '
            'unblock a critical project deadline"].'
        ),
    ),
    Category(
        name="education_logistics_and_goals",
        description=(
            "Extract individual, factual data points as complete, standalone statements. Do not combine "
            "multiple unrelated facts into one chunk. Example: Instead of [\"Master's Bologna, 1 month "
            'notice"], extract ["Master\'s Degree in Computer Science from the University of Bologna."] '
            'and ["Available with a 1-month notice period."].'
        ),
    ),
]


class CategoryName(str, Enum):
    WORK_EXPERIENCE_AND_PROJECTS = "work_experience_and_projects"
    TECHNICAL_AND_HARD_SKILLS = "technical_and_hard_skills"
    SOFT_SKILLS_AND_BEHAVIORAL = "soft_skills_and_behavioral"
    EDUCATION_LOGISTICS_AND_GOALS = "education_logistics_and_goals"
