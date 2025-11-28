from google.adk.agents import Agent, LlmAgent
import json
from FMCopilot.util import load_instruction_from_file
from FMCopilot.tools import filter_rabbitmq_events
from FMCopilot.analysis_tool import calculate_kpi_insights
from FMCopilot.data_analyzer import analyze_exclusive_states_tool

def greet(name: str) -> str:
    return f"Hello! I am FMCopilot, ready to assist with your facility monitoring queries."
rabbitmq_agent = LlmAgent(
    name = "RabbitMQEventFilterAgent",
    model = "gemini-2.0-flash",
    description="An agent that filters RabbitMQ event logs to exclude initial load events.",
    instruction=load_instruction_from_file("FMCopilot/fm_instructions.txt"),
    #FMCopilot/fm_instructions.txt
    tools = [filter_rabbitmq_events],
    output_key="filtered_events")

# Create the Agent 
analysis_agent = LlmAgent(
    name="kpi_analyst",
    model="gemini-2.0-flash",  # or "gemini-1.5-pro" depending on your access
    description="Analyzes factory JSON logs to calculate production KPIs and device performance.",
    instruction=load_instruction_from_file("FMCopilot/analysis_Instruction.txt"),
    tools=[calculate_kpi_insights],
    output_key="kpi_analysis",
)

data_science_agent = LlmAgent(
    name="DataScienceAnalyst",
    model="gemini-2.0-flash",
    description="Analyzes the loaded Exclusive State CSV data to generate plots and statistical summaries.",
    # Note: Use the detailed system instruction defined in the previous response
    instruction=load_instruction_from_file("FMCopilot/exstate_instruction.txt"),
    tools=[analyze_exclusive_states_tool], # Use the correctly initialized tool instance
)
#-----------------
# Chain the agents together
root_agent = LlmAgent(
    name = "FMCopilot",
    model = "gemini-2.0-flash",
    description="An AI assistant that executes a two-step pipeline for Factory Monitoring KPI analysis.",
    instruction=""" 
        Start Conversation with greeting the user.
        You are the FMCopilot orchestrator. Your task is to intelligently route the user's query:

        A. **KPI Log Analysis (JSON Data):** If the user asks for production KPI analysis (e.g., 'Calculate OEE'), execute the two-step sequential pipeline:
           1. Run 'RabbitMQEventFilterAgent' to retrieve data into State['filtered_events'].
           2. Instruct the 'kpi_analyst' agent, passing State['filtered_events'] as the required input argument **filtered_json_data**.
           Finally, present State['kpi_analysis'].

        B. **CSV Data Analysis (Plotting/Summaries):** If the user asks for charts, plots, or summaries based on the 'Exclusive State' CSV data (e.g., 'Plot blocked time per production line', 'Which line has the highest setup duration?'), instruct the **DataScienceAnalyst** agent.

        C. **Greeting:** Use the 'greet' tool for initial conversation only.
    """,
    sub_agents=[rabbitmq_agent, analysis_agent, data_science_agent],
    tools=[greet])