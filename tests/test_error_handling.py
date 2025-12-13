"""
Test Error Handling

Tests for error handling utilities and error recovery mechanisms.
"""

import pytest
import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "qgis-plugin" / "src"))

from utils.error_handling import (
    RTerrainError,
    NetworkError,
    DataFetchError,
    ValidationError,
    LicenseError,
    ExportError,
    GDALError,
    retry,
    handle_errors,
    validate_bbox,
    validate_file_path,
    validate_resolution,
    safe_divide,
    ensure_directory,
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_rterrain_error_basic(self):
        """Test basic RTerrainError."""
        error = RTerrainError("Technical message")
        assert error.message == "Technical message"
        assert error.recoverable is True
        assert "Technical message" in error.user_message

    def test_rterrain_error_with_user_message(self):
        """Test RTerrainError with custom user message."""
        error = RTerrainError(
            "Technical error details",
            user_message="User-friendly message",
            recoverable=False
        )
        assert error.message == "Technical error details"
        assert error.user_message == "User-friendly message"
        assert error.recoverable is False

    def test_network_error(self):
        """Test NetworkError generates appropriate user message."""
        error = NetworkError("Connection timeout")
        assert "network" in error.user_message.lower() or "connection" in error.user_message.lower()

    def test_data_fetch_error(self):
        """Test DataFetchError."""
        error = DataFetchError("Failed to download")
        assert "download" in error.user_message.lower() or "data" in error.user_message.lower()

    def test_validation_error(self):
        """Test ValidationError with field."""
        error = ValidationError("Invalid value", field="bbox")
        assert error.field == "bbox"
        assert "bbox" in error.user_message.lower()

    def test_license_error(self):
        """Test LicenseError."""
        error = LicenseError("License expired")
        assert "license" in error.user_message.lower()

    def test_export_error(self):
        """Test ExportError."""
        error = ExportError("Disk full")
        assert "export" in error.user_message.lower() or "disk" in error.user_message.lower()

    def test_gdal_error(self):
        """Test GDALError."""
        error = GDALError("Geotransform failed")
        assert "geospatial" in error.user_message.lower() or "gdal" in error.user_message.lower()


class TestRetryDecorator:
    """Test retry decorator."""

    def test_retry_success_first_attempt(self):
        """Test function succeeds on first attempt."""
        call_count = [0]

        @retry(max_attempts=3)
        def succeed_immediately():
            call_count[0] += 1
            return "success"

        result = succeed_immediately()
        assert result == "success"
        assert call_count[0] == 1

    def test_retry_success_after_failures(self):
        """Test function succeeds after some failures."""
        call_count = [0]

        @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
        def succeed_on_third_try():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("Not yet")
            return "success"

        result = succeed_on_third_try()
        assert result == "success"
        assert call_count[0] == 3

    def test_retry_max_attempts_exceeded(self):
        """Test retry gives up after max attempts."""
        call_count = [0]

        @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,))
        def always_fail():
            call_count[0] += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError, match="Always fails"):
            always_fail()

        assert call_count[0] == 3

    def test_retry_with_callback(self):
        """Test retry with callback function."""
        callback_calls = []

        def on_retry(attempt, error):
            callback_calls.append((attempt, str(error)))

        call_count = [0]

        @retry(max_attempts=3, delay=0.1, exceptions=(ValueError,), on_retry=on_retry)
        def fail_twice():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError(f"Attempt {call_count[0]}")
            return "success"

        result = fail_twice()
        assert result == "success"
        assert len(callback_calls) == 2
        assert callback_calls[0][0] == 1
        assert "Attempt 1" in callback_calls[0][1]

    def test_retry_exponential_backoff(self):
        """Test exponential backoff timing."""
        import time

        @retry(max_attempts=3, delay=0.05, backoff=2.0, exceptions=(ValueError,))
        def measure_delays():
            raise ValueError("Test")

        start = time.time()
        try:
            measure_delays()
        except ValueError:
            pass
        elapsed = time.time() - start

        # Should have delays of ~0.05s, ~0.1s, ~0.2s = ~0.35s total
        # Allow some margin for execution time
        assert elapsed >= 0.3
        assert elapsed < 1.0


class TestHandleErrorsDecorator:
    """Test handle_errors decorator."""

    def test_handle_errors_returns_default(self):
        """Test function returns default on error."""
        @handle_errors(default_return=[])
        def fail_always():
            raise ValueError("Error!")

        result = fail_always()
        assert result == []

    def test_handle_errors_catches_custom_errors(self):
        """Test catches RTerrainError."""
        @handle_errors(default_return=None)
        def raise_rterrain_error():
            raise NetworkError("Network failed")

        result = raise_rterrain_error()
        assert result is None

    def test_handle_errors_no_error(self):
        """Test function works normally without errors."""
        @handle_errors(default_return=None)
        def succeed():
            return 42

        result = succeed()
        assert result == 42


class TestValidateBbox:
    """Test bbox validation."""

    def test_valid_bbox(self):
        """Test valid bounding box."""
        bbox = (-122.5, 37.7, -122.4, 37.8)
        result = validate_bbox(bbox)
        assert result == bbox

    def test_invalid_longitude_range(self):
        """Test invalid longitude range."""
        with pytest.raises(ValidationError, match="longitude"):
            validate_bbox((200, 0, 210, 10))

    def test_invalid_latitude_range(self):
        """Test invalid latitude range."""
        with pytest.raises(ValidationError, match="latitude"):
            validate_bbox((0, -100, 10, -90))

    def test_min_greater_than_max(self):
        """Test min > max error."""
        with pytest.raises(ValidationError):
            validate_bbox((-120, 40, -125, 45))  # min_lon > max_lon

    def test_bbox_too_small(self):
        """Test bbox too small error."""
        with pytest.raises(ValidationError, match="too small"):
            validate_bbox((0, 0, 0.0001, 0.0001))

    def test_bbox_too_large(self):
        """Test bbox too large error."""
        with pytest.raises(ValidationError, match="too large"):
            validate_bbox((0, 0, 20, 20))

    def test_invalid_bbox_format(self):
        """Test invalid bbox format."""
        with pytest.raises(ValidationError):
            validate_bbox((1, 2, 3))  # Only 3 values

    def test_bbox_with_strings(self):
        """Test bbox with non-numeric values."""
        with pytest.raises(ValidationError):
            validate_bbox(("a", "b", "c", "d"))


class TestValidateFilePath:
    """Test file path validation."""

    def test_valid_new_file_path(self):
        """Test valid path for new file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            result = validate_file_path(str(path))
            assert result == path

    def test_empty_path(self):
        """Test empty path error."""
        with pytest.raises(ValidationError, match="empty"):
            validate_file_path("")

    def test_nonexistent_directory(self):
        """Test nonexistent directory error."""
        with pytest.raises(ValidationError, match="Directory does not exist"):
            validate_file_path("/nonexistent/directory/file.txt")

    def test_must_exist_missing_file(self):
        """Test must_exist with missing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "missing.txt"
            with pytest.raises(ValidationError, match="does not exist"):
                validate_file_path(str(path), must_exist=True)

    def test_must_exist_existing_file(self):
        """Test must_exist with existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "existing.txt"
            path.write_text("test")

            result = validate_file_path(str(path), must_exist=True)
            assert result == path

    def test_wrong_extension(self):
        """Test wrong file extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            with pytest.raises(ValidationError, match="extension"):
                validate_file_path(str(path), extension=".pdf")

    def test_correct_extension(self):
        """Test correct file extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            result = validate_file_path(str(path), extension=".txt")
            assert result == path

    def test_extension_without_dot(self):
        """Test extension specified without dot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            result = validate_file_path(str(path), extension="txt")
            assert result == path


class TestValidateResolution:
    """Test resolution validation."""

    def test_valid_resolution(self):
        """Test valid resolution."""
        result = validate_resolution(30)
        assert result == 30

    def test_valid_resolution_from_list(self):
        """Test valid resolution from allowed list."""
        result = validate_resolution(10, allowed_resolutions=[10, 20, 30])
        assert result == 10

    def test_invalid_resolution_not_in_list(self):
        """Test invalid resolution not in allowed list."""
        with pytest.raises(ValidationError, match="must be one of"):
            validate_resolution(15, allowed_resolutions=[10, 20, 30])

    def test_non_integer_resolution(self):
        """Test non-integer resolution."""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_resolution(30.5)

    def test_negative_resolution(self):
        """Test negative resolution."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_resolution(-30)

    def test_zero_resolution(self):
        """Test zero resolution."""
        with pytest.raises(ValidationError, match="must be positive"):
            validate_resolution(0)


class TestSafeDivide:
    """Test safe division."""

    def test_normal_division(self):
        """Test normal division."""
        result = safe_divide(10, 2)
        assert result == 5.0

    def test_division_by_zero_default(self):
        """Test division by zero returns default."""
        result = safe_divide(10, 0)
        assert result == 0.0

    def test_division_by_zero_custom_default(self):
        """Test division by zero with custom default."""
        result = safe_divide(10, 0, default=999.0)
        assert result == 999.0

    def test_float_division(self):
        """Test float division."""
        result = safe_divide(7.0, 3.0)
        assert abs(result - 2.333333) < 0.001


class TestEnsureDirectory:
    """Test ensure_directory function."""

    def test_create_new_directory(self):
        """Test creating new directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "test_dir"
            result = ensure_directory(str(new_dir))

            assert result.exists()
            assert result.is_dir()

    def test_existing_directory(self):
        """Test with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = ensure_directory(tmpdir)
            assert result.exists()

    def test_create_nested_directories(self):
        """Test creating nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / "a" / "b" / "c"
            result = ensure_directory(str(nested))

            assert result.exists()
            assert result.is_dir()


class TestErrorScenarios:
    """Test realistic error scenarios."""

    def test_network_error_with_retry(self):
        """Test network error is retried."""
        attempts = [0]

        @retry(max_attempts=3, delay=0.1, exceptions=(NetworkError,))
        def flaky_network_call():
            attempts[0] += 1
            if attempts[0] < 3:
                raise NetworkError("Temporary network issue")
            return "success"

        result = flaky_network_call()
        assert result == "success"
        assert attempts[0] == 3

    def test_validation_error_not_retried(self):
        """Test validation errors are not retried."""
        attempts = [0]

        @retry(max_attempts=3, delay=0.1, exceptions=(NetworkError,))
        def invalid_input():
            attempts[0] += 1
            raise ValidationError("Invalid bbox")

        with pytest.raises(ValidationError):
            invalid_input()

        # Should fail immediately without retry
        assert attempts[0] == 1

    def test_graceful_degradation(self):
        """Test graceful degradation with partial failure."""
        @handle_errors(default_return=[])
        def fetch_with_partial_failure():
            results = []

            for i in range(5):
                try:
                    if i == 2:
                        raise DataFetchError("Tile 2 failed")
                    results.append(f"tile_{i}")
                except DataFetchError:
                    # Log and continue
                    continue

            if not results:
                raise DataFetchError("All tiles failed")

            return results

        # Should return partial results
        result = fetch_with_partial_failure()
        assert len(result) == 4
        assert "tile_0" in result
        assert "tile_2" not in result


def test_all_error_types_have_user_messages():
    """Test all error types generate user-friendly messages."""
    errors = [
        RTerrainError("test"),
        NetworkError("test"),
        DataFetchError("test"),
        ValidationError("test"),
        LicenseError("test"),
        ExportError("test"),
        GDALError("test"),
    ]

    for error in errors:
        assert hasattr(error, 'user_message')
        assert len(error.user_message) > 0
        assert error.user_message != error.message


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
