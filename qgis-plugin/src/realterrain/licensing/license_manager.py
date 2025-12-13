"""
License Manager

Handles license validation, storage, and communication with Supabase backend.
"""

import os
import json
import base64
import logging
from datetime import datetime
from typing import Optional, Dict, Tuple
from pathlib import Path

from qgis.PyQt.QtCore import QSettings

from .hardware_fingerprint import get_hardware_fingerprint

# Import error handling utilities
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.error_handling import (
    LicenseError,
    NetworkError,
    ValidationError,
    retry,
    handle_errors,
    handle_network_error
)

# Setup logging
logger = logging.getLogger(__name__)


class LicenseStatus:
    """License status constants."""
    FREE = "free"
    PRO = "pro"
    EXPIRED = "expired"
    INVALID = "invalid"
    NOT_ACTIVATED = "not_activated"


class LicenseManager:
    """Manages license validation and storage."""

    def __init__(self):
        """Initialize the license manager."""
        try:
            self.settings = QSettings("RealTerrainStudio", "QGIS")
            self.hardware_id = get_hardware_fingerprint()

            # License limits (Free tier)
            self.FREE_TIER_LIMITS = {
                "max_area_km2": 10,
                "monthly_exports": 10,
                "max_resolution_m": 30,
            }

            logger.info("License manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize license manager: {e}")
            raise LicenseError(
                f"License system initialization failed: {e}",
                user_message="Could not initialize licensing system. Please restart QGIS."
            )

    @handle_errors(default_return=LicenseStatus.FREE)
    def get_license_status(self) -> str:
        """
        Get current license status.

        Returns:
            str: One of LicenseStatus constants
        """
        try:
            # Check if license key exists
            license_key = self.settings.value("license/key", "")

            if not license_key:
                # No license key - using free version
                logger.debug("No license key found, using free tier")
                return LicenseStatus.FREE

            # Validate stored license
            is_valid, status = self._validate_stored_license()

            if not is_valid:
                logger.warning(f"License validation failed: {status}")
                return status

            logger.debug("Pro license validated successfully")
            return LicenseStatus.PRO

        except Exception as e:
            logger.error(f"Error checking license status: {e}")
            # Default to free tier on error
            return LicenseStatus.FREE

    def activate_license(self, license_key: str) -> Tuple[bool, str]:
        """
        Activate a license key.

        Args:
            license_key: The license key to activate

        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            # Validate input
            if not license_key or len(license_key.strip()) == 0:
                logger.warning("Empty license key provided")
                return False, "License key cannot be empty"

            # Format and validate key format
            license_key = license_key.strip().upper()
            logger.info(f"Attempting to activate license: {self._mask_license_key(license_key)}")

            if not self._validate_key_format(license_key):
                logger.warning(f"Invalid license key format: {self._mask_license_key(license_key)}")
                return False, "Invalid license key format. Expected: XXXX-XXXX-XXXX-XXXX"

            # Validate against Supabase backend (with retry)
            try:
                success, message = self._validate_with_backend(license_key)
            except NetworkError as e:
                logger.error(f"Network error during license validation: {e}")
                return False, e.user_message
            except Exception as e:
                logger.error(f"Unexpected error during license validation: {e}")
                return False, "License validation failed. Please try again later."

            if success:
                # Store license information
                try:
                    self._store_license(license_key)
                    logger.info("License activated and stored successfully")
                    return True, "License activated successfully!"
                except Exception as e:
                    logger.error(f"Failed to store license: {e}")
                    return False, "License validation succeeded but storage failed. Please try again."

            logger.warning(f"License validation failed: {message}")
            return False, message

        except Exception as e:
            logger.exception(f"Unexpected error in activate_license: {e}")
            return False, f"An unexpected error occurred: {str(e)}"

    @handle_errors(default_return=False)
    def deactivate_license(self) -> bool:
        """
        Deactivate the current license.

        Returns:
            bool: True if successful
        """
        try:
            logger.info("Deactivating license")
            self.settings.remove("license/key")
            self.settings.remove("license/activated_date")
            self.settings.remove("license/user_email")
            self.settings.remove("license/hardware_id")
            self.settings.sync()
            logger.info("License deactivated successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to deactivate license: {e}")
            return False

    def get_license_info(self) -> Dict:
        """
        Get detailed license information.

        Returns:
            dict: License information including status, limits, etc.
        """
        status = self.get_license_status()

        info = {
            "status": status,
            "hardware_id": self.hardware_id,
        }

        if status == LicenseStatus.FREE:
            info["tier"] = "Free"
            info["limits"] = self.FREE_TIER_LIMITS
            info["message"] = "Using free version with limited features"

        elif status == LicenseStatus.PRO:
            license_key = self.settings.value("license/key", "")
            activated_date = self.settings.value("license/activated_date", "")
            user_email = self.settings.value("license/user_email", "")

            info["tier"] = "Pro"
            info["license_key"] = self._mask_license_key(license_key)
            info["activated_date"] = activated_date
            info["user_email"] = user_email
            info["limits"] = {
                "max_area_km2": "Unlimited",
                "monthly_exports": "Unlimited",
                "max_resolution_m": "1m (highest available)",
            }
            info["message"] = "Pro license active"

        elif status == LicenseStatus.EXPIRED:
            info["tier"] = "Expired"
            info["message"] = "Your license has expired. Please renew."

        elif status == LicenseStatus.INVALID:
            info["tier"] = "Invalid"
            info["message"] = "License validation failed. Please contact support."

        return info

    def check_export_allowed(self, area_km2: float) -> Tuple[bool, str]:
        """
        Check if an export is allowed based on license.

        Args:
            area_km2: Area size in square kilometers

        Returns:
            Tuple[bool, str]: (allowed, message)
        """
        status = self.get_license_status()

        if status == LicenseStatus.PRO:
            return True, "Export allowed"

        if status == LicenseStatus.FREE:
            if area_km2 > self.FREE_TIER_LIMITS["max_area_km2"]:
                return False, f"Free tier limited to {self.FREE_TIER_LIMITS['max_area_km2']} km². Upgrade to Pro for unlimited exports."

            # TODO: Check monthly export count
            # For now, allow the export
            return True, "Export allowed (Free tier)"

        if status == LicenseStatus.EXPIRED:
            return False, "License expired. Please renew your license."

        if status == LicenseStatus.INVALID:
            return False, "Invalid license. Please contact support."

        return False, "License validation failed"

    def _validate_key_format(self, key: str) -> bool:
        """
        Validate the format of a license key.

        Expected format: XXXX-XXXX-XXXX-XXXX (16 alphanumeric characters)

        Args:
            key: License key to validate

        Returns:
            bool: True if format is valid
        """
        # Remove dashes
        key_clean = key.replace("-", "")

        # Should be 16 characters
        if len(key_clean) != 16:
            return False

        # Should be alphanumeric
        if not key_clean.isalnum():
            return False

        return True

    @retry(
        max_attempts=3,
        delay=1.0,
        backoff=2.0,
        exceptions=(NetworkError,)
    )
    def _validate_with_backend(self, license_key: str) -> Tuple[bool, str]:
        """
        Validate license key with Supabase backend.

        Args:
            license_key: License key to validate

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            NetworkError: If network operation fails after retries
        """
        logger.debug(f"Validating license with backend: {self._mask_license_key(license_key)}")

        # TODO: Implement actual Supabase validation
        # This would make an API call to Supabase:
        # import requests
        # response = requests.post(
        #     f"{SUPABASE_URL}/rest/v1/rpc/validate_license",
        #     json={"license_key": license_key, "hardware_id": self.hardware_id},
        #     headers={"apikey": SUPABASE_KEY}
        # )

        # For now, use mock validation for testing
        try:
            # Simulate network request
            import time
            time.sleep(0.1)  # Simulate API delay

            # Mock: Accept any key that starts with "PRO-"
            if license_key.startswith("PRO-"):
                logger.debug("Mock validation: PRO key accepted")
                return True, "License validated successfully"

            # Mock: Accept specific test keys
            test_keys = [
                "TEST-1234-5678-ABCD",
                "DEMO-ABCD-1234-EFGH",
            ]

            if license_key in test_keys:
                logger.debug("Mock validation: Test key accepted")
                return True, "License validated successfully"

            logger.debug("Mock validation: Invalid key")
            return False, "Invalid license key. Please check and try again."

        except Exception as e:
            logger.error(f"Backend validation error: {e}")
            raise NetworkError(
                f"Failed to validate license with backend: {e}",
                user_message="Cannot connect to license server. Check your internet connection."
            )

    def _validate_stored_license(self) -> Tuple[bool, str]:
        """
        Validate the stored license.

        Returns:
            Tuple[bool, str]: (is_valid, status)
        """
        license_key = self.settings.value("license/key", "")

        if not license_key:
            return False, LicenseStatus.NOT_ACTIVATED

        # Validate format
        if not self._validate_key_format(license_key):
            return False, LicenseStatus.INVALID

        # TODO: Periodically re-validate with backend
        # For now, trust stored license
        return True, LicenseStatus.PRO

    def _store_license(self, license_key: str):
        """
        Store license information locally.

        Args:
            license_key: License key to store
        """
        self.settings.setValue("license/key", license_key)
        self.settings.setValue("license/activated_date", datetime.now().isoformat())
        self.settings.setValue("license/hardware_id", self.hardware_id)

        # TODO: Store user email from backend response
        self.settings.setValue("license/user_email", "user@example.com")

        self.settings.sync()

    def _mask_license_key(self, key: str) -> str:
        """
        Mask a license key for display.

        Args:
            key: License key to mask

        Returns:
            str: Masked key (e.g., XXXX-XXXX-****-****)
        """
        if not key:
            return ""

        # Remove dashes
        key_clean = key.replace("-", "")

        if len(key_clean) < 8:
            return "****-****-****-****"

        # Show first 8 chars, mask the rest
        visible = key_clean[:8]
        masked = visible[:4] + "-" + visible[4:8] + "-****-****"

        return masked

    def is_first_run(self) -> bool:
        """
        Check if this is the first run of the plugin.

        Returns:
            bool: True if first run
        """
        first_run = self.settings.value("app/first_run", True, type=bool)
        return first_run

    def mark_first_run_complete(self):
        """Mark that the first run has been completed."""
        self.settings.setValue("app/first_run", False)
        self.settings.sync()
