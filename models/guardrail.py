from pydantic import BaseModel

class HasSensitiveInformation(BaseModel):
    """
    Model representing the result of a guardrail check.
    
    Attributes:
        has_sensitive_information (bool): True if sensitive information was detected
        reasoning (str): Explanation of why the content was flagged as sensitive
    """
    has_sensitive_information: bool
    reasoning: str 