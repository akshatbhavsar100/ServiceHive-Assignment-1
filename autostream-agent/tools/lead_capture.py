"""
tools/lead_capture.py
Mock lead capture tool for AutoStream agent.
"""

import json
from datetime import datetime


def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    """
    Mock API function to capture a qualified lead.
    In production, this would POST to a CRM like HubSpot or Salesforce.

    Args:
        name: The lead's full name
        email: The lead's email address
        platform: The creator platform (YouTube, Instagram, TikTok, etc.)

    Returns:
        dict with success status and confirmation details
    """
    timestamp = datetime.now().isoformat()

    # Simulate API call
    print("\n" + "=" * 50)
    print("🎯 LEAD CAPTURED SUCCESSFULLY")
    print("=" * 50)
    print(f"  Name     : {name}")
    print(f"  Email    : {email}")
    print(f"  Platform : {platform}")
    print(f"  Timestamp: {timestamp}")
    print("=" * 50 + "\n")

    return {
        "success": True,
        "lead_id": f"LEAD-{abs(hash(email)) % 100000:05d}",
        "name": name,
        "email": email,
        "platform": platform,
        "captured_at": timestamp,
        "message": f"Lead captured successfully: {name}, {email}, {platform}"
    }


def validate_email(email: str) -> bool:
    """Basic email validation."""
    return "@" in email and "." in email.split("@")[-1]


def validate_platform(platform: str) -> bool:
    """Check if the platform is a recognised creator platform."""
    known_platforms = [
        "youtube", "instagram", "tiktok", "twitter", "x",
        "facebook", "linkedin", "twitch", "snapchat", "pinterest"
    ]
    return any(p in platform.lower() for p in known_platforms)
