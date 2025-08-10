# backend/app/services/mappers.py

# -*- coding: utf-8 -*-
import re
from backend.api.models import PreparationAnalysis, QuestionCategory


def parse_markdown_to_preparation_analysis(markdown_text: str) -> PreparationAnalysis:
    """
    Parses Markdown text from Agent 3's output into a PreparationAnalysis object.

    The expected Markdown structure is:

    ## План интервью с кандидатом: [Имя кандидата]

    ### Технические вопросы:
    * Вопрос 1
    * Вопрос 2
    * ...

    ### Поведенческие вопросы:
    * Вопрос 1
    * Вопрос 2
    * ...

    ### Ключевые рекомендации и области для внимания:
    * Рекомендация 1
    * Рекомендация 2
    * ...
    """

    name_match = re.search(r'## План интервью с кандидатом: (.*)', markdown_text)
    candidate_name = name_match.group(1).strip() if name_match else "Unknown Candidate"

    sections = re.split(r'### ', markdown_text)

    questions = []
    key_topics = []

    for section in sections:
        if section.startswith('Технические вопросы:'):
            questions_text = section.replace('Технические вопросы:', '').strip()
            technical_questions = [q.strip() for q in questions_text.split('* ') if q.strip()]
            if technical_questions:
                questions.append(QuestionCategory(category="Technical Questions", questions=technical_questions))

        elif section.startswith('Поведенческие вопросы:'):
            questions_text = section.replace('Поведенческие вопросы:', '').strip()
            behavioral_questions = [q.strip() for q in questions_text.split('* ') if q.strip()]
            if behavioral_questions:
                questions.append(QuestionCategory(category="Behavioral Questions", questions=behavioral_questions))

        elif section.startswith('Ключевые рекомендации и области для внимания:'):
            topics_text = section.replace('Ключевые рекомендации и области для внимания:', '').strip()
            key_topics = [t.strip() for t in topics_text.split('* ') if t.strip()]

    return PreparationAnalysis(
        message=f"Interview preparation plan for {candidate_name} created successfully.",
        keyTopics=key_topics,
        suggestedQuestions=questions,
    )
