from pydantic import BaseModel

class CompanyInfo(BaseModel):
    """
    Model for company information.

    Attributes:
    mission_statement (str): The company's mission statement.
    values (str): The company's values.
    history (str): The company's history.
    """
    mission_statement: str
    values: str
    history: str
