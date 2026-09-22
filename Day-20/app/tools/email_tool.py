"""
Day 20 — Email Tool
Handles safe email composition, address syntax validation, and simulated outbound dispatch.
Clearly labeled as a local simulation (no live SMTP transmission or mailbox access).
"""

import re
import uuid
import time
import os
import json
from email.message import EmailMessage
from typing import Dict, Any, Optional
from ..schemas import ToolResult, ToolDefinition, ToolParameter


EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
)


def _validate_email_syntax(address: str) -> bool:
    if not address or not isinstance(address, str):
        return False
    return bool(EMAIL_REGEX.match(address.strip()))


def _get_drafts_dir() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    drafts_dir = os.path.join(base_dir, "data", "drafts")
    os.makedirs(drafts_dir, exist_ok=True)
    return drafts_dir


def email_tool(
    recipient: str,
    subject: str,
    body: str,
    action: str = "validate"
) -> ToolResult:
    """
    Performs email operations:
    - 'validate': Checks recipient address format and payload fields.
    - 'draft': Constructs a genuine RFC 822 MIME message and persists it to disk as an .eml draft.
    - 'simulate_send': Validates and appends message to outbox log.
    - 'list_drafts': Lists saved drafts stored on disk.
    """
    act = str(action).strip().lower()
    drafts_dir = _get_drafts_dir()

    if act == "list_drafts":
        draft_files = [f for f in os.listdir(drafts_dir) if f.endswith(".json")]
        drafts = []
        for df in draft_files:
            try:
                with open(os.path.join(drafts_dir, df), "r", encoding="utf-8") as f:
                    drafts.append(json.load(f))
            except Exception:
                continue
        return ToolResult.ok(
            "email_tool",
            data={"action": "list_drafts", "total_drafts": len(drafts), "drafts": drafts}
        )

    # 1. Recipient syntax validation
    if not recipient or not recipient.strip():
        return ToolResult.fail("email_tool", "Recipient email address cannot be empty.")

    clean_recipient = recipient.strip()
    if not _validate_email_syntax(clean_recipient):
        return ToolResult.fail(
            "email_tool",
            f"Invalid recipient email address format: '{clean_recipient}'. Must conform to standard user@domain.tld syntax.",
            metadata={"recipient": clean_recipient, "error_code": "INVALID_EMAIL_SYNTAX"}
        )

    # 2. Subject & body validation
    if not subject or not subject.strip():
        return ToolResult.fail("email_tool", "Email subject line cannot be empty.")
    if not body or not body.strip():
        return ToolResult.fail("email_tool", "Email body content cannot be empty.")

    clean_subject = subject.strip()
    clean_body = body.strip()

    # 3. Action execution
    if act == "validate":
        return ToolResult.ok(
            "email_tool",
            data={
                "action": "validate",
                "recipient": clean_recipient,
                "is_valid_syntax": True,
                "subject_length": len(clean_subject),
                "body_word_count": len(clean_body.split()),
                "status": "ready_to_send"
            }
        )

    elif act == "draft":
        draft_id = f"DRAFT-{uuid.uuid4().hex[:6].upper()}"
        created_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Construct genuine RFC 822 MIME message
        msg = EmailMessage()
        msg["From"] = "system@linkific.internal"
        msg["To"] = clean_recipient
        msg["Subject"] = clean_subject
        msg["Date"] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        msg["Message-ID"] = f"<{draft_id.lower()}@linkific.internal>"
        msg.set_content(clean_body)

        # Write .eml file to disk
        eml_path = os.path.join(drafts_dir, f"{draft_id}.eml")
        with open(eml_path, "wb") as f:
            f.write(msg.as_bytes())

        # Write metadata .json to disk
        meta = {
            "draft_id": draft_id,
            "recipient": clean_recipient,
            "subject": clean_subject,
            "body": clean_body,
            "status": "draft_saved",
            "eml_file": os.path.basename(eml_path),
            "created_at": created_iso
        }
        json_path = os.path.join(drafts_dir, f"{draft_id}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return ToolResult.ok(
            "email_tool",
            data={
                "action": "draft",
                "draft_id": draft_id,
                "recipient": clean_recipient,
                "subject": clean_subject,
                "body": clean_body,
                "status": "draft_saved",
                "saved_file": eml_path,
                "created_at": created_iso
            },
            metadata={"persisted_on_disk": True}
        )

    elif act in ("simulate_send", "send"):
        message_id = f"MSG-{uuid.uuid4().hex[:8].upper()}"
        dispatch_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Log outbound message event to outbox.log
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        outbox_log = os.path.join(base_dir, "data", "outbox.log")
        with open(outbox_log, "a", encoding="utf-8") as f:
            f.write(f"[{dispatch_time}] ID={message_id} TO={clean_recipient} SUBJ=\"{clean_subject}\"\n")

        return ToolResult.ok(
            "email_tool",
            data={
                "action": "simulate_send",
                "message_id": message_id,
                "recipient": clean_recipient,
                "subject": clean_subject,
                "body_preview": clean_body[:100] + ("..." if len(clean_body) > 100 else ""),
                "status": "simulated_delivered",
                "timestamp": dispatch_time,
                "outbox_log": outbox_log
            },
            metadata={"logged_to_outbox": True}
        )

    else:
        return ToolResult.fail(
            "email_tool",
            f"Unsupported email action '{action}'. Supported actions: 'validate', 'draft', 'simulate_send', 'list_drafts'.",
            metadata={"action": action}
        )


EMAIL_DEFINITION = ToolDefinition(
    name="email_tool",
    description="Validates recipient address, constructs RFC 822 MIME emails, saves drafts to disk, and logs outbound dispatch.",
    parameters={
        "recipient": ToolParameter(
            name="recipient",
            type="string",
            description="Recipient email address (e.g. 'mentor@linkific.internal').",
            required=True
        ),
        "subject": ToolParameter(
            name="subject",
            type="string",
            description="Subject heading of the email message.",
            required=True
        ),
        "body": ToolParameter(
            name="body",
            type="string",
            description="Plain-text body content of the email.",
            required=True
        ),
        "action": ToolParameter(
            name="action",
            type="string",
            description="Operation to perform: 'validate', 'draft', 'simulate_send', or 'list_drafts'.",
            required=False,
            default="validate",
            enum=["validate", "draft", "simulate_send", "list_drafts"]
        )
    },
    returns={
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "recipient": {"type": "string"},
            "status": {"type": "string"}
        }
    },
    is_mock=False
)
