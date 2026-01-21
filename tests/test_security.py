"""Security and unit tests for orionapi.

Tests security features, error handling, and bug fixes.
"""
import time
from unittest.mock import Mock, patch

import pytest
import requests

from orionapi import (
    AuthenticationError,
    EclipseAPI,
    NotFoundError,
    OrionAPI,
    OrionAPIError,
    RateLimiter,
)


class TestCredentialSecurity:
    """Test that credentials are not stored in memory."""

    def test_orion_credentials_not_stored(self):
        """Verify OrionAPI doesn't store plaintext credentials."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="testuser", pwd="testpass")

            # Credentials should NOT be stored
            assert not hasattr(api, "usr")
            assert not hasattr(api, "pwd")
            assert not hasattr(api, "username")
            assert not hasattr(api, "password")

            # Verify not in __dict__
            assert "usr" not in api.__dict__
            assert "pwd" not in api.__dict__

    def test_eclipse_credentials_not_stored(self):
        """Verify EclipseAPI doesn't store plaintext credentials."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="testuser", pwd="testpass")

            # Credentials should NOT be stored
            assert not hasattr(api, "usr")
            assert not hasattr(api, "pwd")
            assert not hasattr(api, "username")
            assert not hasattr(api, "password")

            # Verify not in __dict__
            assert "usr" not in api.__dict__
            assert "pwd" not in api.__dict__


class TestRateLimiting:
    """Test rate limiting functionality."""

    def test_rate_limiter_basic(self):
        """Test basic rate limiting works."""
        limiter = RateLimiter(calls_per_second=5)  # 5 calls/sec = 0.2s between calls

        # First call should be immediate
        start = time.time()
        limiter.wait()
        first_duration = time.time() - start
        assert first_duration < 0.05  # Should be nearly instant

        # Second call should wait ~0.2 seconds
        start = time.time()
        limiter.wait()
        second_duration = time.time() - start
        assert 0.15 <= second_duration <= 0.35  # Allow some variance

    def test_rate_limiter_disabled(self):
        """Test rate limiting can be disabled."""
        limiter = RateLimiter(calls_per_second=0)

        # Should not wait at all
        start = time.time()
        for _ in range(10):
            limiter.wait()
        duration = time.time() - start

        assert duration < 0.1  # All calls should be instant

    def test_rate_limiter_multiple_calls(self):
        """Test rate limiting over multiple calls."""
        limiter = RateLimiter(calls_per_second=10)  # 10 calls/sec

        start = time.time()
        for _ in range(5):
            limiter.wait()
        duration = time.time() - start

        # 5 calls at 10/sec should take ~0.4 seconds
        assert 0.3 <= duration <= 0.6

    def test_api_uses_rate_limiter(self):
        """Test that API client uses rate limiter."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass", rate_limit=5)

            assert hasattr(api, "_rate_limiter")
            assert api._rate_limiter.calls_per_second == 5


class TestLogSanitization:
    """Test log sanitization for sensitive data."""

    def test_sanitize_dict_with_token(self):
        """Test token is redacted from dict."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            data = {"username": "john", "token": "secret123", "data": "public"}

            sanitized = api._sanitize_for_logging(data)

            assert sanitized["username"] == "john"
            assert sanitized["token"] == "***REDACTED***"
            assert sanitized["data"] == "public"

    def test_sanitize_dict_with_password(self):
        """Test password is redacted from dict."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            data = {"username": "john", "password": "secret123"}

            sanitized = api._sanitize_for_logging(data)

            assert sanitized["username"] == "john"
            assert sanitized["password"] == "***REDACTED***"

    def test_sanitize_nested_dict(self):
        """Test nested dicts are sanitized recursively."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            data = {
                "user": "john",
                "auth": {"token": "secret123", "api_key": "key456"},
                "public": "data",
            }

            sanitized = api._sanitize_for_logging(data)

            assert sanitized["user"] == "john"
            assert sanitized["auth"]["token"] == "***REDACTED***"
            assert sanitized["auth"]["api_key"] == "***REDACTED***"
            assert sanitized["public"] == "data"

    def test_sanitize_list(self):
        """Test lists are sanitized."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            data = [
                {"username": "john", "token": "secret1"},
                {"username": "jane", "token": "secret2"},
            ]

            sanitized = api._sanitize_for_logging(data)

            assert sanitized[0]["username"] == "john"
            assert sanitized[0]["token"] == "***REDACTED***"
            assert sanitized[1]["username"] == "jane"
            assert sanitized[1]["token"] == "***REDACTED***"

    def test_sanitize_various_sensitive_keys(self):
        """Test various sensitive key patterns are redacted."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            data = {
                "access_token": "secret1",
                "accessToken": "secret2",
                "api_key": "secret3",
                "apiKey": "secret4",
                "pwd": "secret5",
                "session": "secret6",
                "authorization": "secret7",
                "my_secret_key": "secret8",  # Contains 'secret'
                "safe_data": "public",
            }

            sanitized = api._sanitize_for_logging(data)

            # All sensitive keys should be redacted
            for key in data.keys():
                if key != "safe_data":
                    assert sanitized[key] == "***REDACTED***", f"Key '{key}' was not redacted"

            assert sanitized["safe_data"] == "public"


class TestTimeouts:
    """Test request timeout functionality."""

    def test_timeout_parameter_accepted(self):
        """Test that timeout parameter is accepted by api_request."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            # Mock the request function directly
            mock_req = Mock(return_value=Mock(ok=True, json=lambda: {}))

            with patch.object(api._rate_limiter, "wait"), \
                 patch.object(api, "_get_auth_header", return_value={}):
                api.api_request("http://test.com", req_func=mock_req, timeout=60)

                # Verify timeout was passed
                assert "timeout" in mock_req.call_args[1]
                assert mock_req.call_args[1]["timeout"] == 60


class TestSSLVerification:
    """Test SSL verification configuration."""

    def test_default_ssl_verification_enabled(self):
        """Test SSL verification is enabled by default."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            assert api.verify_ssl is True
            assert api.ca_bundle is None

    def test_ssl_verification_can_be_disabled(self):
        """Test SSL verification can be disabled."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass", verify_ssl=False)

            assert api.verify_ssl is False

    def test_custom_ca_bundle(self):
        """Test custom CA bundle can be specified."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass", ca_bundle="/path/to/ca.crt")

            assert api.ca_bundle == "/path/to/ca.crt"

    def test_ssl_verification_passed_to_requests(self):
        """Test SSL verification setting is passed to requests."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass", verify_ssl=False)

            # Mock the request function directly
            mock_req = Mock(return_value=Mock(ok=True, json=lambda: {}))

            with patch.object(api._rate_limiter, "wait"), \
                 patch.object(api, "_get_auth_header", return_value={}):
                api.api_request("http://test.com", req_func=mock_req)

                # Verify SSL verification was passed
                assert "verify" in mock_req.call_args[1]
                assert mock_req.call_args[1]["verify"] is False


class TestAuthenticationErrors:
    """Test authentication error handling."""

    def test_orion_login_401_error(self):
        """Test OrionAPI raises AuthenticationError on 401."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 401
            mock_response.reason = "Unauthorized"
            mock_response.json.return_value = {"message": "Invalid credentials"}
            mock_get.return_value = mock_response

            with pytest.raises(AuthenticationError, match="Login failed"):
                OrionAPI(usr="bad", pwd="wrong")

    def test_eclipse_login_403_error(self):
        """Test EclipseAPI raises AuthenticationError on 403."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 403
            mock_response.reason = "Forbidden"
            mock_response.json.return_value = {"message": "Access denied"}
            mock_get.return_value = mock_response

            with pytest.raises(AuthenticationError, match="Login failed"):
                EclipseAPI(usr="bad", pwd="wrong")

    def test_token_extraction_error(self):
        """Test error when token is missing from response."""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.ok = True
            mock_response.json.return_value = {}  # No token!
            mock_get.return_value = mock_response

            with pytest.raises(AuthenticationError, match="Invalid response"):
                OrionAPI(usr="user", pwd="pass")


class TestAPIErrors:
    """Test API error handling for various HTTP status codes."""

    def test_404_not_found_error(self):
        """Test NotFoundError raised on 404."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            # Mock the request function to return 404
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 404
            mock_response.reason = "Not Found"
            mock_response.json.return_value = {"message": "Resource not found"}
            mock_req = Mock(return_value=mock_response)

            with patch.object(api._rate_limiter, "wait"), \
                 patch.object(api, "_get_auth_header", return_value={}):
                with pytest.raises(NotFoundError, match="Resource not found"):
                    api.api_request("http://test.com/missing", req_func=mock_req)

    def test_500_server_error(self):
        """Test OrionAPIError raised on 500."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            # Mock the request function to return 500
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 500
            mock_response.reason = "Internal Server Error"
            mock_response.json.return_value = {"message": "Server error"}
            mock_req = Mock(return_value=mock_response)

            with patch.object(api._rate_limiter, "wait"), \
                 patch.object(api, "_get_auth_header", return_value={}):
                with pytest.raises(OrionAPIError, match="500.*Server error"):
                    api.api_request("http://test.com", req_func=mock_req)

    def test_error_without_json_body(self):
        """Test error handling when response has no JSON."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            # Mock the request function to return error without JSON
            mock_response = Mock()
            mock_response.ok = False
            mock_response.status_code = 500
            mock_response.reason = "Internal Server Error"
            mock_response.text = "HTML error page"
            mock_response.json.side_effect = ValueError("No JSON")
            mock_req = Mock(return_value=mock_response)

            with patch.object(api._rate_limiter, "wait"), \
                 patch.object(api, "_get_auth_header", return_value={}):
                with pytest.raises(OrionAPIError, match="HTML error page"):
                    api.api_request("http://test.com", req_func=mock_req)


class TestInputValidation:
    """Test input validation for search methods."""

    def test_search_clients_empty_string_rejected(self):
        """Test search_clients rejects empty search term."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="non-empty string"):
                api.search_clients("")

    def test_search_clients_whitespace_only_rejected(self):
        """Test search_clients rejects whitespace-only search term."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="non-empty string"):
                api.search_clients("   ")

    def test_search_clients_non_string_rejected(self):
        """Test search_clients rejects non-string search term."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="non-empty string"):
                api.search_clients(123)

    def test_search_clients_negative_top_rejected(self):
        """Test search_clients rejects negative top value."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="positive integer"):
                api.search_clients("test", top=-1)

    def test_search_clients_zero_top_rejected(self):
        """Test search_clients rejects zero top value."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="positive integer"):
                api.search_clients("test", top=0)

    def test_search_clients_non_integer_top_rejected(self):
        """Test search_clients rejects non-integer top value."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="positive integer"):
                api.search_clients("test", top="10")


class TestFilePathValidation:
    """Test file path validation for security."""

    def test_parse_security_set_file_not_found(self):
        """Test parse_security_set_file rejects non-existent file."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(FileNotFoundError, match="File not found"):
                api.parse_security_set_file("/nonexistent/path/file.txt")

    def test_export_security_set_invalid_parent_directory(self):
        """Test export rejects path with non-existent parent directory."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "get_security_set", return_value={"name": "Test", "securities": []}
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(FileNotFoundError, match="Parent directory does not exist"):
                api.export_security_set_to_file(123, "/nonexistent/dir/file.txt")


class TestBugFixes:
    """Test specific bugs that were fixed."""

    def test_create_set_aside_default_min_max_amounts(self):
        """Test create_set_aside works with default min/max amounts.

        Bug: float(None) caused TypeError when min_amount/max_amount not provided.
        Fix: Changed defaults from None to 0.0
        """
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "get_internal_account_id", return_value=123
        ), patch.object(EclipseAPI, "_get_auth_header", return_value={}), patch.object(
            EclipseAPI, "_maybe_wait_for_analytics"
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1}
                mock_post.return_value = mock_response

                # This should NOT raise TypeError
                result = api.create_set_aside(account_number="12345", amount=1000)

                # Verify the request was made with proper values
                mock_post.assert_called_once()
                request_json = mock_post.call_args[1]["json"]

                assert request_json["minCashAmount"] == 0.0
                assert request_json["maxCashAmount"] == 0.0
                assert request_json["cashAmount"] == 1000.0

    def test_create_set_aside_expire_type_transaction_uses_tolerance(self):
        """Test create_set_aside uses tolerance value for transaction expiration.

        Bug: When expire_type=2 (Transaction), was setting expire_value to
        expire_trans_type (the type ID) instead of expire_trans_tol (the tolerance value).
        Fix: Changed to use expire_trans_tol
        """
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "get_internal_account_id", return_value=123
        ), patch.object(EclipseAPI, "_get_auth_header", return_value={}), patch.object(
            EclipseAPI, "_maybe_wait_for_analytics"
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1}
                mock_post.return_value = mock_response

                # Create set-aside with Transaction expiration
                api.create_set_aside(
                    account_number="12345",
                    amount=1000,
                    expire_type="Transaction",
                    expire_trans_tol=50,  # The tolerance value
                    expire_trans_type=1,  # The transaction type ID
                )

                # Verify expirationValue is set to tolerance, not type ID
                mock_post.assert_called_once()
                request_json = mock_post.call_args[1]["json"]

                # Should use tolerance value (50), not type ID (1)
                assert request_json["expirationValue"] == 50
                assert request_json["toleranceValue"] == 50
                assert request_json["transactionTypeId"] == 1
