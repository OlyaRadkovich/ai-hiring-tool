from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents import Agent
from .agent_1_data_parser import agent_1_data_parser
from .agent_2_grader import agent_2_grader
from .agent_3_report_generator import agent_3_report_generator


def create_pre_interview_pipeline(api_key: str):
    agent_1 = Agent(
        name=agent_1_data_parser.name,
        model=agent_1_data_parser.model,
        description=agent_1_data_parser.description,
        instruction=agent_1_data_parser.instruction,
        tools=agent_1_data_parser.tools
    )

    agent_2 = Agent(
        name=agent_2_grader.name,
        model=agent_2_grader.model,
        description=agent_2_grader.description,
        instruction=agent_2_grader.instruction,
        tools=agent_2_grader.tools
    )

    agent_3 = Agent(
        name=agent_3_report_generator.name,
        model=agent_3_report_generator.model,
        description=agent_3_report_generator.description,
        instruction=agent_3_report_generator.instruction,
        tools=agent_3_report_generator.tools
    )

    return SequentialAgent(
        name="pre_interview_pipeline",
        description="Пайплайн для анализа данных кандидата и подготовки к интервью.",
        sub_agents=[agent_1, agent_2, agent_3]
    )
