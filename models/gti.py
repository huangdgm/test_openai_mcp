"""
GTI (Google Threat Intelligence) data models for query results and responses.

This module contains Pydantic models for structuring GTI query results
and responses in the enhanced MCP orchestrator system.
"""

from pydantic import BaseModel

class GTIQuery(BaseModel):
    """
    Model representing a Google Threat Intelligence query result.
    
    This model structures the results from GTI queries, including
    the original query, the response from GTI, and source identification.
    
    Attributes:
        query (str): The original query sent to GTI
        result (str): The response from GTI
        source (str): Source identifier, defaults to "Google Threat Intelligence"
    """
    query: str
    result: str
    source: str = "Google Threat Intelligence" 