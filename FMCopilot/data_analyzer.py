import pandas as pd


# --- Configuration Constants ---
# IMPORTANT: Update this path if the CSV file is not in the same directory.
CSV_FILE_PATH = r"C:\Users\Administrator\source\PersonalRepo\FMCopilot\FMCopilot\ExclusiveState_Solihull_FA3_Last_3_Months.csv"
STATE_NAMES = [
    'Cycling', 'Starved', 'Blocked', 'Waiting Aux', 'Paused', 'Overcycle', 
    'Production Hold', 'Bypass', 'Break', 'Waiting Attention', 'Repair in Progress', 
    'Manual Mode', 'Manual Intervention', 'Tool Change', 'Emergency Stop', 'Setup'
]

# --- Helper Function: Duration Parser (Same as before) ---

def parse_duration(duration_str):
    """
    Converts duration strings (e.g., '13504:51' or '13504:51:00') to total seconds.
    The format 'H:M' is interpreted as 'TotalHours:Minutes'.
    """
    if pd.isna(duration_str) or duration_str in ('00:00', '0'):
        return 0

    duration_str = str(duration_str).strip()
    parts = duration_str.split(':')

    try:
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
        elif len(parts) == 2:
            hours, minutes = map(int, parts)
            seconds = 0
        else:
            return 0

        total_seconds = (hours * 3600) + (minutes * 60) + seconds
        return total_seconds
    except ValueError:
        return 0

# --- The Monolithic ADK Tool Function ---

def analyze_exclusive_states_tool(analysis_description: str, chart_type: str = 'bar'):
    """
    Loads, cleans, and analyzes the Exclusive State CSV data to generate plots 
    and statistical summaries based on the user's request. 
    
    The function will autonomously generate Python code (using pandas/matplotlib/seaborn) 
    to perform the requested analysis, save the plot to a file (e.g., 'analysis_plot.png'), 
    and return a string describing the plot and findings.
    
    The data uses 'Production Line' for grouping and duration metrics are in 
    columns suffixed with '(Sec)'.
    
    Args:
        analysis_description: A natural language description of the analysis or plot 
                              requested (e.g., 'Compare total blocked time across 
                              all production lines').
        chart_type: The desired type of plot (e.g., 'bar', 'line', 'pie').
    
    Returns:
        A string containing the path to the saved plot image and a summary of the findings.
    """
    
    # 1. Load and Pre-process Data (This logic runs every time the tool is called)
    try:
        df = pd.read_csv(CSV_FILE_PATH, header=5)
    except FileNotFoundError:
        return f"Error: CSV file not found at {CSV_FILE_PATH}. Cannot perform analysis."
    
    raw_cols = df.columns.tolist()
    column_map = {'Description': 'Production Line'}
    
    for state in STATE_NAMES:
        try:
            duration_col = state
            occurrence_col = raw_cols[raw_cols.index(state) + 1]
            column_map[duration_col] = f'{state} Duration (Raw)'
            column_map[occurrence_col] = f'{state} Occurrence'
        except ValueError:
            continue

    column_map['Total'] = 'Total Duration (Raw)'
    column_map['Occ.'] = 'Total Occurrence'
    
    cols_to_drop = [col for col in df.columns if col.startswith('Unnamed:') and col not in column_map.keys()]
    df = df.drop(columns=cols_to_drop, errors='ignore')
    df = df.rename(columns=column_map)
    
    duration_raw_cols = [col for col in df.columns if col.endswith('(Raw)')]
    
    for raw_col in duration_raw_cols:
        new_sec_col = raw_col.replace(' (Raw)', ' (Sec)')
        df[new_sec_col] = df[raw_col].apply(parse_duration)
        df = df.drop(columns=[raw_col])
    
    df = df.dropna(subset=['Production Line'])
    
    # NOTE FOR LLM: The DataFrame object 'df' is now fully cleaned and available
    # for code execution based on the 'analysis_description'.
    
    # 2. Tool Execution (The LLM generates the code based on the docstring/state)
    # This return string guides the ADK system to generate and execute the code.
    return f"Agent will generate code using the cleaned 'df' to fulfill the request: '{analysis_description}' using a {chart_type} chart."