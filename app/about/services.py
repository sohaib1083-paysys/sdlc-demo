from app.about.models import CompanyInfo
from app.about.database import get_company_info_from_db

def get_company_info():
    """
    Get the company information from the database.

    Returns:
    CompanyInfo: The company information.
    """
    company_info = get_company_info_from_db()
    return CompanyInfo(
        mission_statement=company_info["mission_statement"],
        values=company_info["values"],
        history=company_info["history"]
    )
