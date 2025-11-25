from google.adk.agents import Agent, LlmAgent

import json
from FMCopilot.util import load_instruction_from_file
from FMCopilot.tools import filter_rabbitmq_events
from FMCopilot.analysis_tool import calculate_kpi_insights

rabbitmq_agent = LlmAgent(
    name = "RabbitMQEventFilterAgent",
    model = "gemini-2.0-flash",
    description="An agent that filters RabbitMQ event logs to exclude initial load events.",
    instruction=load_instruction_from_file("FMCopilot/fm_instructions.txt"),
    #FMCopilot/fm_instructions.txt
    tools = [filter_rabbitmq_events],
    output_key="filtered_events")

# Create the Agent instance
analysis_agent = LlmAgent(
    name="kpi_analyst",
    model="gemini-2.0-flash",  # or "gemini-1.5-pro" depending on your access
    description="Analyzes factory JSON logs to calculate production KPIs and device performance.",
    instruction=load_instruction_from_file("FMCopilot/analysis_instruction.txt"),
    tools=[calculate_kpi_insights],
    output_key="kpi_analysis",
)
#-----------------
# Chain the agents together
root_agent = LlmAgent(
    name = "FMCopilot",
    model = "gemini-2.0-flash",
    description="An AI assistant that executes a two-step pipeline for Factory Monitoring KPI analysis.",
    instruction=""" You are the FMCopilot orchestrator. Your task is to execute the full KPI analysis pipeline in two sequential steps to answer the user's query:

STEP 1: **Data Extraction.** Run 'RabbitMQEventFilterAgent' to retrieve the raw log data. This agent's tool will output a clean JSON string of logs into State['filtered_events'].

STEP 2: **Analysis and Reporting.** Instruct the 'kpi_analyst' agent to execute its analysis tool. You MUST pass the complete content of **State['filtered_events']** as the input argument named **filtered_json_data** to the kpi_analyst tool.

Finally, present the output stored in State['kpi_analysis'] to the user.
""",
    sub_agents=[rabbitmq_agent, analysis_agent])