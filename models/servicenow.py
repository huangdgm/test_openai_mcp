"""
ServiceNow data models for query results and responses.

This module contains Pydantic models for structuring ServiceNow query results
and responses in the enhanced MCP orchestrator system.
"""

from pydantic import BaseModel

class ServiceNowQuery(BaseModel):
    """
    Model representing a ServiceNow query result.
    
    This model structures the results from ServiceNow queries, including
    the original query, the response from ServiceNow, and source identification.
    
    Attributes:
        query (str): The original query sent to ServiceNow
        result (str): The response from ServiceNow
        source (str): Source identifier, defaults to "ServiceNow"
    """
    query: str
    result: str
    source: str = "ServiceNow" 