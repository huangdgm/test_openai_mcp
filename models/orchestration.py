"""
Orchestration data models for service routing decisions.

This module contains Pydantic models for structuring orchestration decisions
in the enhanced MCP orchestrator system.
"""

from pydantic import BaseModel

class ServiceDecision(BaseModel):
    """
    Model representing the orchestrator's decision about which services to query.
    
    This model structures the decisions made by the orchestrator agent about
    which specialized services should handle a user query based on analysis
    of the query content and context.
    
    Attributes:
        servicenow (bool): Whether ServiceNow should be queried
        gti (bool): Whether Google Threat Intelligence should be queried
        opensearch (bool): Whether OpenSearch should be queried
        reasoning (str): Explanation of the decision
    """
    servicenow: bool
    gti: bool
    opensearch: bool
    reasoning: str 