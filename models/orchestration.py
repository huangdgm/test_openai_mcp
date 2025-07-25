from pydantic import BaseModel

class ServiceDecision(BaseModel):
    """
    Model representing the orchestrator's decision about which services to query.
    
    Attributes:
        servicenow (bool): Whether ServiceNow should be queried
        gti (bool): Whether Google Threat Intelligence should be queried
        reasoning (str): Explanation of the decision
    """
    servicenow: bool
    gti: bool
    reasoning: str 