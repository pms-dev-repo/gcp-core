def status_badge(status: str) -> str:
    css_class = {
        "Ready": "status-ready",
        "Generated": "status-generated",
        "Reviewed": "status-reviewed",
        "Sent": "status-sent",
        "Missing email": "status-error",
    }.get(status, "status-ready")
    return f'<span class="status-badge {css_class}">{status}</span>'
