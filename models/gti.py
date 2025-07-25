from pydantic import BaseModel

class GTIQuery(BaseModel):
    """
    Model representing a Google Threat Intelligence query result.
    
    Attributes:
        query (str): The original query sent to GTI
        result (str): The response from GTI
        source (str): Source identifier, defaults to "Google Threat Intelligence"
    """
    query: str
    result: str
    source: str = "Google Threat Intelligence" 