import json
from datetime import datetime
from typing import Dict, Any, List

def calculate_kpi_insights(filtered_json_data: str) -> Dict[str, Any]:
    """
    Performs complex time-series and aggregation analysis on filtered log data.
    
    Args:
        filtered_json_data: A JSON string containing the list of filtered events.

    Returns:
        A dictionary containing structured analysis results (ready for LLM interpretation).
    """
    try:
        logs = json.loads(filtered_json_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON input received by analysis tool."}

    # --- Core Analysis Logic ---
    production_events = [
        log for log in logs 
        if log.get("EventName") == "ProductionTotalPartCount"
    ]
    
    if not production_events:
        return {"error": "No 'ProductionTotalPartCount' events found for analysis."}

    # Sort events by timestamp for rate calculation
    production_events.sort(key=lambda x: datetime.strptime(x["EventOccured"], "%Y-%m-%dT%H:%M:%S"))

    # 1. Production Rate Analysis
    first_event = production_events[0]
    last_event = production_events[-1]
    
    start_value = first_event["EventArgs"]["Value"]
    end_value = last_event["EventArgs"]["Value"]
    total_increase = end_value - start_value
    
    time_delta = datetime.strptime(last_event["EventOccured"], "%Y-%m-%dT%H:%M:%S") - \
             datetime.strptime(first_event["EventOccured"], "%Y-%m-%dT%H:%M:%S")
    total_minutes = time_delta.total_seconds() / 60
    
    # 2. Device Performance Aggregation
    device_production: Dict[str, float] = {}
    for event in production_events:
        device = event["DeviceName"]
        value = event["EventArgs"]["Value"]
        # Use the latest value for aggregation (assuming logs report cumulative count)
        device_production[device] = value 

    # 3. Trend Identification (Simplified)
    is_stalling = False
    if len(production_events) >= 2 and production_events[-1]["EventArgs"]["Value"] == production_events[-2]["EventArgs"]["Value"]:
        is_stalling = True

    # --- Return Structured Data ---
    analysis_result = {
        "overall_summary": {
            "total_logs_analyzed": len(production_events),
            "total_time_window_minutes": round(total_minutes, 2),
            "total_part_increase": round(total_increase, 2),
            "average_rate_per_minute": round(total_increase / total_minutes, 2) if total_minutes > 0 else 0
        },
        "device_performance": device_production,
        "warnings": {
            "stalling_detected": is_stalling,
            "stalling_device": last_event["DeviceName"] if is_stalling else None
        }
    }
    
    return analysis_result