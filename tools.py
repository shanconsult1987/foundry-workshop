from data import REQUESTS


def get_request(request_id: str):
    """Return one citizen request."""

    for request in REQUESTS:
        if request["id"] == request_id:
            return request

    return {
        "error": f"Request {request_id} was not found."
    }


def search_requests(category: str):
    """Find requests by category."""

    results = [
        request
        for request in REQUESTS
        if request["category"].lower() == category.lower()
    ]

    return results


def get_summary():
    """Return request statistics."""

    total = len(REQUESTS)

    open_count = sum(
        1
        for request in REQUESTS
        if request["status"] == "Open"
    )

    in_progress = sum(
        1
        for request in REQUESTS
        if request["status"] == "In Progress"
    )

    resolved = sum(
        1
        for request in REQUESTS
        if request["status"] == "Resolved"
    )

    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved,
    }

# Microsoft Foundry hosted web search tool
WEB_SEARCH_TOOL = {
    "type": "web_search"
}