from fastapi import Response
from fastapi.responses import HTMLResponse

def handle_404():
    """
    Handle 404 errors.

    Returns:
    HTMLResponse: The 404 error page.
    """
    return HTMLResponse(content="<h1>404 Error</h1>", status_code=404)

def handle_no_internet():
    """
    Handle no internet connection errors.

    Returns:
    HTMLResponse: The no internet connection error page.
    """
    return HTMLResponse(content="<h1>No Internet Connection</h1>", status_code=500)
