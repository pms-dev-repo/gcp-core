from modules.shared_placeholder import render_module_placeholder


def render() -> None:
    render_module_placeholder(
        "Confirmation Letters",
        "Generate reservation confirmation letters using hotel-specific templates.",
        (
            "Select a reservation",
            "Choose a confirmation template",
            "Generate DOCX or PDF",
            "Review and send by email",
        ),
    )
