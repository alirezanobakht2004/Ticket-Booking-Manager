from db.db import create_report, get_ticket_owner_person_id
import logging

def submit_report_service(current_user_id: int, ticket_id: int, report_type: str, report_text: str):
    """
    Service to handle the submission of a new ticket issue report.
    """
    # Optional but recommended: Check if the user reporting the issue actually owns the ticket.
    ticket_owner_id = get_ticket_owner_person_id(ticket_id)
    if not ticket_owner_id or ticket_owner_id != current_user_id:
        raise PermissionError("You can only report issues for your own tickets.")

    # Validate inputs
    if not report_type or not report_text:
        raise ValueError("Report type and text are required.")

    # Create the report in the database
    report_id = create_report(current_user_id, ticket_id, report_type, report_text)
    
    if not report_id:
        raise Exception("Failed to create the report in the database.")

    return {
        "message": "Report submitted successfully.",
        "report_id": report_id,
        "ticket_id": ticket_id,
        "report_type": report_type
    }
