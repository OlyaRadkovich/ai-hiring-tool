# -*- coding: utf-8 -*-
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents import Agent

from .agent_1_data_parser import agent_1_data_parser
from .agent_2_profiler import agent_2_profiler
from .agent_3_plan_generator import agent_3_plan_generator


def create_pre_interview_pipeline(api_key: str):
    """
    Создает и возвращает пайплайн агентов,
    передавая API-ключ каждому агенту.
    """
    agent_1 = Agent(
        name=agent_1_data_parser.name,
        model=agent_1_data_parser.model,
        description=agent_1_data_parser.description,
        instruction=agent_1_data_parser.instruction,
        tools=agent_1_data_parser.tools,
        api_key=api_key
    )

    agent_2 = Agent(
        name=agent_2_profiler.name,
        model=agent_2_profiler.model,
        description=agent_2_profiler.description,
        instruction=agent_2_profiler.instruction,
        tools=agent_2_profiler.tools,
        api_key=api_key
    )

    agent_3 = Agent(
        name=agent_3_plan_generator.name,
        model=agent_3_plan_generator.model,
        description=agent_3_plan_generator.description,
        instruction=agent_3_plan_generator.instruction,
        tools=agent_3_plan_generator.tools,
        api_key=api_key
    )

    return SequentialAgent(
        name="pre_interview_pipeline",
        description="Пайплайн для анализа данных кандидата и подготовки к интервью.",
        sub_agents=[agent_1, agent_2, agent_3]
    )
