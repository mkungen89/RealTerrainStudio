"""
Error Handling Utilities

Centralized error handling, retry logic, and user-friendly error messages
for RealTerrain Studio.
"""

import functools
import time
import logging
from typing import Optional, Callable, Tuple, Type, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RTerrainError(Exception):
    """Base exception for all RealTerrain Studio errors."""

    def __init__(self, message: str, user_message: Optional[str] = None, recoverable: bool = True):
        """
        Initialize RTerrainError.

        Args:
            message: Technical error message (for logs)
            user_message: User-friendly message (shown in UI)
            recoverable: Whether user can recover from this error
        """
        super().__init__(message)
        self.message = message
        self.user_message = user_message or self._generate_user_message(message)
        self.recoverable = recoverable

    def _generate_user_message(self, tech_message: str) -> str:
        """Generate a user-friendly message from technical message."""
        return f"An error occurred: {tech_message[:100]}..."


class NetworkError(RTerrainError):
    """Raised when network operations fail."""

    def _generate_user_message(self, tech_message: str) -> str:
        return (
            "Network connection problem. Please check your internet connection "
            "and try again. If the problem persists, the server may be busy."
        )


class DataFetchError(RTerrainError):
    """Raised when data fetching fails."""

    def _generate_user_message(self, tech_message: str) -> str:
        return (
            "Failed to download required data. This could be due to:\n"
            "• Internet connection issues\n"
            "• Data source temporarily unavailable\n"
            "• Selected area has no data coverage\n\n"
            "Please try again in a few minutes."
        )


class ValidationError(RTerrainError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(message, recoverable=True)
        self.field = field

    def _generate_user_message(self, tech_message: str) -> str:
        if self.field:
            return f"Invalid {self.field}: {tech_message}"
        return f"Validation error: {tech_message}"


class LicenseError(RTerrainError):
    """Raised when license validation fails."""

    def _generate_user_message(self, tech_message: str) -> str:
        return (
            "License validation failed. Please check:\n"
            "• License key is entered correctly\n"
            "• License hasn't expired\n"
            "• You haven't exceeded activation limit (3 devices)\n\n"
            "Contact support if the problem continues."
        )


class ExportError(RTerrainError):
    """Raised when export operations fail."""

    def _generate_user_message(self, tech_message: str) -> str:
        return (
            "Export failed. Common causes:\n"
            "• Not enough disk space\n"
            "• File permissions issue\n"
            "• Selected area too large\n\n"
            "Try exporting to a different location or reducing the area size."
        )


class GDALError(RTerrainError):
    """Raised when GDAL operations fail."""

    def _generate_user_message(self, tech_message: str) -> str:
        return (
            "Geospatial processing error. This usually means:\n"
            "• Corrupted data file\n"
            "• Unsupported file format\n"
            "• GDAL library issue\n\n"
            "Try downloading the data again or contact support."
        )


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    Decorator to retry a function with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each attempt (exponential backoff)
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function(attempt_number, exception)

    Example:
        >>> @retry(max_attempts=3, delay=1.0, exceptions=(NetworkError,))
        ... def fetch_data():
        ...     # This will retry up to 3 times on NetworkError
        ...     return requests.get(url)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay

            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    if attempt == max_attempts:
                        # Final attempt failed - raise the exception
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Log retry attempt
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )

                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt, e)
                        except Exception as callback_err:
                            logger.warning(f"Retry callback failed: {callback_err}")

                    # Wait before retrying
                    time.sleep(current_delay)

                    # Increase delay for next attempt (exponential backoff)
                    current_delay *= backoff

            # Should never reach here, but just in case
            return func(*args, **kwargs)

        return wrapper
    return decorator


def handle_errors(
    default_return: Any = None,
    log_traceback: bool = True,
    user_message: Optional[str] = None,
    show_dialog: bool = False
):
    """
    Decorator to catch and handle errors gracefully.

    Args:
        default_return: Value to return if an error occurs
        log_traceback: Whether to log full traceback
        user_message: User-friendly error message to show
        show_dialog: Whether to show error dialog (QGIS)

    Example:
        >>> @handle_errors(default_return=[], user_message="Failed to load data")
        ... def load_data():
        ...     # If this fails, return [] and show user message
        ...     return fetch_data()
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except RTerrainError as e:
                # Our custom errors already have user messages
                logger.error(f"{func.__name__} error: {e.message}")
                if log_traceback:
                    logger.exception("Full traceback:")

                if show_dialog:
                    _show_error_dialog(e.user_message)

                return default_return

            except Exception as e:
                # Unexpected error - log and show generic message
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                if log_traceback:
                    logger.exception("Full traceback:")

                msg = user_message or f"An unexpected error occurred: {str(e)}"
                if show_dialog:
                    _show_error_dialog(msg)

                return default_return

        return wrapper
    return decorator


def validate_bbox(bbox: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
    """
    Validate and normalize a bounding box.

    Args:
        bbox: Bounding box (min_lon, min_lat, max_lon, max_lat)

    Returns:
        Normalized bounding box

    Raises:
        ValidationError: If bbox is invalid
    """
    try:
        min_lon, min_lat, max_lon, max_lat = bbox
    except (TypeError, ValueError) as e:
        raise ValidationError(
            f"Bounding box must be a tuple of 4 numbers: {e}",
            field="bounding_box"
        )

    # Validate longitude
    if not (-180 <= min_lon < max_lon <= 180):
        raise ValidationError(
            f"Invalid longitude range: {min_lon:.4f} to {max_lon:.4f}. "
            f"Longitude must be between -180 and 180, and min < max.",
            field="longitude"
        )

    # Validate latitude
    if not (-90 <= min_lat < max_lat <= 90):
        raise ValidationError(
            f"Invalid latitude range: {min_lat:.4f} to {max_lat:.4f}. "
            f"Latitude must be between -90 and 90, and min < max.",
            field="latitude"
        )

    # Check minimum size (avoid tiny areas)
    width = max_lon - min_lon
    height = max_lat - min_lat

    if width < 0.001 or height < 0.001:
        raise ValidationError(
            f"Bounding box too small: {width:.6f}° × {height:.6f}°. "
            f"Minimum size is 0.001° × 0.001° (~100m × 100m).",
            field="area_size"
        )

    # Check maximum size (prevent huge downloads)
    if width > 10 or height > 10:
        raise ValidationError(
            f"Bounding box too large: {width:.2f}° × {height:.2f}°. "
            f"Maximum size is 10° × 10° (~1100km × 1100km). "
            f"Try splitting into smaller areas.",
            field="area_size"
        )

    return (min_lon, min_lat, max_lon, max_lat)


def validate_file_path(path: str, must_exist: bool = False, extension: Optional[str] = None) -> Path:
    """
    Validate a file path.

    Args:
        path: File path to validate
        must_exist: Whether file must already exist
        extension: Required file extension (e.g., '.tif')

    Returns:
        Path object

    Raises:
        ValidationError: If path is invalid
    """
    if not path or len(path.strip()) == 0:
        raise ValidationError("File path cannot be empty", field="file_path")

    file_path = Path(path)

    # Check if parent directory exists
    if not file_path.parent.exists():
        raise ValidationError(
            f"Directory does not exist: {file_path.parent}",
            field="directory"
        )

    # Check if file exists (if required)
    if must_exist and not file_path.exists():
        raise ValidationError(
            f"File does not exist: {file_path}",
            field="file_path"
        )

    # Check extension
    if extension:
        if not extension.startswith('.'):
            extension = f'.{extension}'

        if file_path.suffix.lower() != extension.lower():
            raise ValidationError(
                f"Invalid file extension. Expected {extension}, got {file_path.suffix}",
                field="file_extension"
            )

    # Check write permissions (for output files)
    if not must_exist:
        try:
            # Try to create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise ValidationError(
                f"No permission to write to: {file_path.parent}",
                field="permissions"
            )

    return file_path


def validate_resolution(resolution: int, allowed_resolutions: Optional[list] = None) -> int:
    """
    Validate resolution parameter.

    Args:
        resolution: Resolution in meters
        allowed_resolutions: List of allowed resolutions (e.g., [10, 20, 30])

    Returns:
        Validated resolution

    Raises:
        ValidationError: If resolution is invalid
    """
    if not isinstance(resolution, int):
        raise ValidationError(
            f"Resolution must be an integer, got {type(resolution).__name__}",
            field="resolution"
        )

    if resolution <= 0:
        raise ValidationError(
            f"Resolution must be positive, got {resolution}",
            field="resolution"
        )

    if allowed_resolutions and resolution not in allowed_resolutions:
        raise ValidationError(
            f"Resolution must be one of {allowed_resolutions}, got {resolution}",
            field="resolution"
        )

    return resolution


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if division by zero.

    Args:
        numerator: Number to divide
        denominator: Number to divide by
        default: Value to return if denominator is zero

    Returns:
        Result of division or default
    """
    if denominator == 0:
        logger.warning(f"Division by zero: {numerator} / {denominator}, returning {default}")
        return default

    return numerator / denominator


def ensure_directory(path: str) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object

    Raises:
        ExportError: If directory cannot be created
    """
    dir_path = Path(path)

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    except PermissionError:
        raise ExportError(
            f"No permission to create directory: {dir_path}",
            user_message=f"Cannot create directory '{dir_path}'. Check file permissions."
        )

    except Exception as e:
        raise ExportError(
            f"Failed to create directory {dir_path}: {e}",
            user_message=f"Cannot create directory. Error: {str(e)}"
        )


def _show_error_dialog(message: str):
    """
    Show error dialog to user (QGIS).

    Args:
        message: Error message to display
    """
    try:
        from qgis.PyQt.QtWidgets import QMessageBox

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("RealTerrain Studio - Error")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    except ImportError:
        # If QGIS not available (e.g., during testing), just log
        logger.error(f"Error dialog: {message}")


def log_function_call(func):
    """
    Decorator to log function calls with arguments and results.

    Useful for debugging and tracking execution flow.

    Example:
        >>> @log_function_call
        ... def calculate_area(width, height):
        ...     return width * height
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Log function call
        args_str = ', '.join(repr(arg) for arg in args)
        kwargs_str = ', '.join(f"{k}={v!r}" for k, v in kwargs.items())
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))

        logger.debug(f"Calling {func.__name__}({all_args})")

        # Execute function
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result!r}")
            return result

        except Exception as e:
            logger.debug(f"{func.__name__} raised: {type(e).__name__}: {e}")
            raise

    return wrapper


# Convenience functions for common error scenarios

def handle_network_error(func: Callable, *args, **kwargs):
    """
    Execute a function and convert network errors to NetworkError.

    Args:
        func: Function to execute
        *args: Arguments for function
        **kwargs: Keyword arguments for function

    Returns:
        Function result

    Raises:
        NetworkError: If network operation fails
    """
    import requests

    try:
        return func(*args, **kwargs)

    except requests.exceptions.ConnectionError as e:
        raise NetworkError(
            f"Connection error: {e}",
            user_message="Cannot connect to server. Check your internet connection."
        )

    except requests.exceptions.Timeout as e:
        raise NetworkError(
            f"Request timeout: {e}",
            user_message="Server is taking too long to respond. Try again later."
        )

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 'unknown'
        raise NetworkError(
            f"HTTP error {status_code}: {e}",
            user_message=f"Server error (code {status_code}). The service may be temporarily unavailable."
        )

    except requests.exceptions.RequestException as e:
        raise NetworkError(
            f"Request error: {e}",
            user_message="Network request failed. Please try again."
        )


def handle_gdal_error(func: Callable, *args, **kwargs):
    """
    Execute a function and convert GDAL errors to GDALError.

    Args:
        func: Function to execute
        *args: Arguments for function
        **kwargs: Keyword arguments for function

    Returns:
        Function result

    Raises:
        GDALError: If GDAL operation fails
    """
    try:
        return func(*args, **kwargs)

    except Exception as e:
        # GDAL errors don't have a specific exception type
        error_msg = str(e).lower()

        if any(keyword in error_msg for keyword in ['gdal', 'geotransform', 'projection', 'raster']):
            raise GDALError(
                f"GDAL operation failed: {e}",
                user_message="Geospatial data processing error. The data file may be corrupted."
            )

        # Not a GDAL error - re-raise
        raise


# Error reporting

def create_error_report(error: Exception, context: Optional[Dict] = None) -> Dict:
    """
    Create a detailed error report for debugging.

    Args:
        error: Exception that occurred
        context: Optional context information (e.g., function args, state)

    Returns:
        dict: Error report with details
    """
    import traceback
    import sys

    report = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'traceback': traceback.format_exc(),
        'timestamp': time.time(),
    }

    # Add RTerrainError specific info
    if isinstance(error, RTerrainError):
        report['user_message'] = error.user_message
        report['recoverable'] = error.recoverable

    # Add context if provided
    if context:
        report['context'] = context

    # Add system info
    report['system'] = {
        'platform': sys.platform,
        'python_version': sys.version,
    }

    return report


def save_error_report(error: Exception, output_path: str, context: Optional[Dict] = None):
    """
    Save error report to file for debugging.

    Args:
        error: Exception that occurred
        output_path: Path to save report
        context: Optional context information
    """
    import json

    report = create_error_report(error, context)

    try:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Error report saved to: {output_path}")

    except Exception as e:
        logger.error(f"Failed to save error report: {e}")
