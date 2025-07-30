"""
Guardrail data models for sensitive information detection.

This module contains Pydantic models for structuring guardrail check results
in the enhanced MCP orchestrator system.
"""

from pydantic import BaseModel

class HasSensitiveInformation(BaseModel):
    """
    Model representing the result of a guardrail check.
    
    This model structures the results from guardrail checks, indicating whether
    sensitive information was detected in a user query and providing reasoning
    for the decision.
    
    Attributes:
        has_sensitive_information (bool): True if sensitive information was detected
        reasoning (str): Explanation of why the content was flagged as sensitive
    """
    has_sensitive_information: bool
    reasoning: str 