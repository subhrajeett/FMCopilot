import json
from typing import Dict, Any, List

def filter_rabbitmq_events(file_path: str) -> str:
    """
    Reads a log file (assumed to be a JSON array of log entries), extracts the 
    RabbitMQ event messages, and filters out all 'KPIInitialLoad' events.

    The function assumes the RabbitMQ message is an embedded JSON string 
    in the log content, following the marker 'RabbitMQ [SendMessage] -- Sent message: '.

    Args:
        file_path: The path to the log file (e.g., 'downloaded-logs-20251123-091108.json').

    Returns:
        A JSON string (List[Dict]) of the extracted RabbitMQ message payloads 
        that are not 'KPIInitialLoad' events.
    """
    
    SENT_MESSAGE_MARKER = "RabbitMQ [SendMessage] -- Sent message: "
    EVENT_TO_EXCLUDE = "KPIInitialLoad"
    
    filtered_events = []
    
    try:
        # 1. Read the JSON file content
        with open(file_path, 'r') as f:
            log_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return "[]" # Return an empty JSON array string on error
    except json.JSONDecodeError as e:
        print(f"Error: Could not decode JSON from '{file_path}'. Details: {e}")
        return "[]" 
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "[]"

    # 2. Iterate through each log entry
    for entry in log_data:
        try:
            # Extract the raw log string
            log_content = entry.get("jsonPayload", {}).get("log", "")
            
            # 3. Check for the RabbitMQ message marker
            if SENT_MESSAGE_MARKER in log_content:
                # Find the start of the embedded JSON message
                start_index = log_content.find(SENT_MESSAGE_MARKER) + len(SENT_MESSAGE_MARKER)
                
                # The message ends right before ' to exchange:'
                end_marker = " to exchange:"
                end_index = log_content.find(end_marker, start_index)
                
                if end_index == -1:
                    # If ' to exchange:' is not found, take the rest of the string
                    message_payload_str = log_content[start_index:].strip()
                else:
                    # Extract the embedded JSON string
                    message_payload_str = log_content[start_index:end_index].strip()
                    
                # 4. Parse the embedded JSON string into a dictionary
                # The json.loads handles the escaped quotes from the outer JSON.
                event_message = json.loads(message_payload_str)
                
                # 5. Filter the event based on EventName
                if event_message.get("EventName") != EVENT_TO_EXCLUDE:
                    filtered_events.append(event_message)
                    
        except json.JSONDecodeError:
            # Skip log entries with malformed embedded JSON
            continue
        except Exception:
            # Skip any other problematic log entries
            continue

    # --- CRITICAL FIX FOR ADK INTEGRATION ---
    # Convert the list of Python dictionaries into a clean JSON string
    return json.dumps(filtered_events)