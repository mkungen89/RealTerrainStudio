"""
Hardware Fingerprint Generation

Generates a unique hardware ID for license validation.
Uses non-invasive system information that remains stable.
"""

import hashlib
import platform
import uuid
from typing import Optional


def get_hardware_fingerprint() -> str:
    """
    Generate a unique hardware fingerprint for this machine.

    Uses multiple stable hardware identifiers to create a unique hash.
    This fingerprint should remain constant across reboots but may change
    if significant hardware changes occur.

    Returns:
        str: 32-character hexadecimal hardware fingerprint
    """
    components = []

    # MAC address (most stable identifier)
    try:
        mac = uuid.getnode()
        components.append(str(mac))
    except Exception:
        pass

    # Machine name
    try:
        machine = platform.node()
        if machine:
            components.append(machine)
    except Exception:
        pass

    # Processor info
    try:
        processor = platform.processor()
        if processor:
            components.append(processor)
    except Exception:
        pass

    # System info
    try:
        system = platform.system()
        if system:
            components.append(system)
    except Exception:
        pass

    # Platform
    try:
        plat = platform.platform()
        if plat:
            components.append(plat)
    except Exception:
        pass

    # If we couldn't get any components, use a fallback
    if not components:
        components.append("fallback-unknown-machine")

    # Combine all components and hash
    combined = "|".join(components)
    fingerprint = hashlib.sha256(combined.encode()).hexdigest()[:32]

    return fingerprint


def get_machine_info() -> dict:
    """
    Get human-readable machine information for display.

    Returns:
        dict: Machine information including platform, processor, etc.
    """
    info = {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "node": platform.node(),
        "fingerprint": get_hardware_fingerprint()
    }

    return info


def validate_fingerprint(fingerprint: str) -> bool:
    """
    Validate that a fingerprint has the correct format.

    Args:
        fingerprint: The fingerprint to validate

    Returns:
        bool: True if valid format, False otherwise
    """
    if not fingerprint or not isinstance(fingerprint, str):
        return False

    if len(fingerprint) != 32:
        return False

    # Check if it's hexadecimal
    try:
        int(fingerprint, 16)
        return True
    except ValueError:
        return False
