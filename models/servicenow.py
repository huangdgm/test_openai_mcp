from pydantic import BaseModel

class ServiceNowQuery(BaseModel):
    """
    Model representing a ServiceNow query result.
    
    Attributes:
        query (str): The original query sent to ServiceNow
        result (str): The response from ServiceNow
        source (str): Source identifier, defaults to "ServiceNow"
    """
    query: str
    result: str
    source: str = "ServiceNow" 