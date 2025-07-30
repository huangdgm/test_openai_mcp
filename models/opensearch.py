"""
OpenSearch data models for query results and responses.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class OpenSearchQuery(BaseModel):
    """
    Represents a query made to OpenSearch and its results.
    
    Attributes:
        query: The original query string
        result: The response from OpenSearch
        source: The source system (OpenSearch)
    """
    query: str
    result: str
    source: str = "OpenSearch" 