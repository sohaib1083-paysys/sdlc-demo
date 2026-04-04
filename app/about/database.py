import psycopg2

def get_company_info_from_db():
    """
    Get the company information from the database.

    Returns:
    dict: The company information.
    """
    conn = psycopg2.connect(
        database="company_db",
        user="company_user",
        password="company_password",
        host="company_host",
        port="company_port"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM company_info")
    company_info = cur.fetchone()
    conn.close()
    return {
        "mission_statement": company_info[0],
        "values": company_info[1],
        "history": company_info[2]
    }
