from pydantic import BaseModel

class VisualizationResult(BaseModel):
    """
    A Pydantic model representing the result of a visualization analysis.
    
    This model is used by the visualization agent to structure its output when
    analyzing data from ServiceNow and/or Google Threat Intelligence sources.
    The agent generates a summary of findings, determines the best visualization
    type, and provides code snippets for creating the visualization.
    
    Attributes:
        summary (str): A natural language summary of the key findings from the data analysis.
        visualization_type (str): The recommended type of visualization for the data.
        code_snippet (str): Python code or markdown that can be used to generate the visualization.
    """
    summary: str
    visualization_type: str
    code_snippet: str = "" 