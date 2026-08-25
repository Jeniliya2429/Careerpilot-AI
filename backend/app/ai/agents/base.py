"""
Base definitions and helper functions for Multi-Agent workers.
"""
from typing import Dict, Any, List
from datetime import datetime, timezone


def create_agent_log(agent_name: str, action: str, details: str | Dict[str, Any]) -> Dict[str, Any]:
    """Helper to generate standardized agent execution log entries."""
    return {
        "agent": agent_name,
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "details": details,
    }


def append_agent_log(state: Dict[str, Any], agent_name: str, action: str, details: str | Dict[str, Any]) -> List[Dict[str, Any]]:
    """Returns updated agent_logs list with a new log entry appended."""
    existing = state.get("agent_logs") or []
    new_log = create_agent_log(agent_name, action, details)
    return existing + [new_log]
