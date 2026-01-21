"""Feature tests for orionapi update operations and analytics.

Tests for medium-priority features identified in coverage analysis.
"""
import time
from unittest.mock import Mock, patch

import pytest

from orionapi import EclipseAPI, OrionAPI


class TestOrionUpdateOperations:
    """Test OrionAPI update operations."""

    def test_update_client(self):
        """Test updating a client/household."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ), patch.object(OrionAPI, "_translate_custom_fields", return_value={"name": "Updated Name"}):
            api = OrionAPI(usr="test", pwd="pass")

            with patch("requests.put") as mock_put:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 123, "name": "Updated Name"}
                mock_put.return_value = mock_response

                result = api.update_client(123, {"name": "Updated Name"})

                mock_put.assert_called_once()
                assert result["id"] == 123
                assert result["name"] == "Updated Name"

    def test_update_registration(self):
        """Test updating a registration."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ), patch.object(
            OrionAPI, "_translate_custom_fields", return_value={"name": "Updated Registration"}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch("requests.put") as mock_put:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 456, "name": "Updated Registration"}
                mock_put.return_value = mock_response

                result = api.update_registration(456, {"name": "Updated Registration"})

                mock_put.assert_called_once()
                assert result["id"] == 456
                assert result["name"] == "Updated Registration"

    def test_update_orion_account(self):
        """Test updating an Orion account."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ), patch.object(
            OrionAPI, "_translate_custom_fields", return_value={"accountType": "IRA"}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch("requests.put") as mock_put:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 789, "accountType": "IRA"}
                mock_put.return_value = mock_response

                result = api.update_orion_account(789, {"accountType": "IRA"})

                mock_put.assert_called_once()
                assert result["id"] == 789
                assert result["accountType"] == "IRA"


# EclipseAPI doesn't have update operations yet, removed invalid test


class TestEclipseAnalytics:
    """Test Eclipse analytics methods."""

    def test_get_analytics_status_running(self):
        """Test getting analytics status when running."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            # Mock api_request to return status
            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {"isAnalysisRunning": True, "progress": 45}
                mock_api_request.return_value = mock_response

                result = api.get_analytics_status()

                mock_api_request.assert_called_once()
                assert result["isAnalysisRunning"] is True
                assert result["progress"] == 45

    def test_get_analytics_status_complete(self):
        """Test getting analytics status when complete."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            # Mock api_request to return status
            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {"isAnalysisRunning": False}
                mock_api_request.return_value = mock_response

                result = api.get_analytics_status()

                mock_api_request.assert_called_once()
                assert result["isAnalysisRunning"] is False

    def test_run_analytics(self):
        """Test triggering analytics run."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            # Mock api_request to return status
            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {"status": "started"}
                mock_api_request.return_value = mock_response

                result = api.run_analytics()

                mock_api_request.assert_called_once()
                assert result["status"] == "started"

    def test_wait_for_analytics_immediate_completion(self):
        """Test wait_for_analytics when already complete."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "_get_auth_header", return_value={}
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "get_analytics_status", return_value={"isAnalysisRunning": False}):
                start = time.time()
                result = api.wait_for_analytics(poll_interval=0.1)
                duration = time.time() - start

                assert result is True
                assert duration < 0.5  # Should return immediately

    def test_wait_for_analytics_polls_until_complete(self):
        """Test wait_for_analytics polls until complete."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "_get_auth_header", return_value={}
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            # Simulate analytics completing after 2 polls
            call_count = [0]

            def mock_status():
                call_count[0] += 1
                return {"isAnalysisRunning": call_count[0] < 3}  # Complete on 3rd call

            with patch.object(api, "get_analytics_status", side_effect=mock_status):
                start = time.time()
                result = api.wait_for_analytics(poll_interval=0.1, timeout=10)
                duration = time.time() - start

                assert result is True
                assert call_count[0] == 3  # Should have polled 3 times
                assert 0.15 <= duration <= 0.5  # ~0.2s (2 intervals)

    def test_wait_for_analytics_timeout(self):
        """Test wait_for_analytics raises TimeoutError."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "_get_auth_header", return_value={}
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(
                api, "get_analytics_status", return_value={"isAnalysisRunning": True}
            ):  # Never completes
                with pytest.raises(TimeoutError, match="did not complete within"):
                    api.wait_for_analytics(poll_interval=0.1, timeout=0.3)

    def test_maybe_wait_for_analytics_when_sync_true(self):
        """Test _maybe_wait_for_analytics waits when sync=True."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "_get_auth_header", return_value={}
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(
                api, "wait_for_analytics", return_value=True
            ) as mock_wait:
                api._maybe_wait_for_analytics(sync=True)

                mock_wait.assert_called_once()

    def test_maybe_wait_for_analytics_when_sync_false(self):
        """Test _maybe_wait_for_analytics skips when sync=False."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "_get_auth_header", return_value={}
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(
                api, "wait_for_analytics", return_value=True
            ) as mock_wait:
                api._maybe_wait_for_analytics(sync=False)

                mock_wait.assert_not_called()


class TestCreateSetAsideExtended:
    """Extended tests for create_set_aside with various configurations."""

    def test_create_set_aside_with_description(self):
        """Test create_set_aside with description."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "get_internal_account_id", return_value=123
        ), patch.object(EclipseAPI, "_get_auth_header", return_value={}), patch.object(
            EclipseAPI, "_maybe_wait_for_analytics"
        ):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1, "description": "Emergency Fund"}
                mock_post.return_value = mock_response

                result = api.create_set_aside(
                    account_number="12345",
                    amount=5000,
                    min_amount=4000,
                    max_amount=6000,
                    description="Emergency Fund",
                )

                mock_post.assert_called_once()
                request_json = mock_post.call_args[1]["json"]

                assert request_json["cashAmount"] == 5000.0
                assert request_json["minCashAmount"] == 4000.0
                assert request_json["maxCashAmount"] == 6000.0
                assert request_json["description"] == "Emergency Fund"

    def test_create_set_aside_percentage_type(self):
        """Test create_set_aside with percentage cash type."""
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

                result = api.create_set_aside(
                    account_number="12345", amount=10, cash_type="%"  # Percentage
                )

                mock_post.assert_called_once()
                request_json = mock_post.call_args[1]["json"]

                assert request_json["cashAmountTypeId"] == 2  # Percentage type ID

    def test_create_set_aside_date_expiration(self):
        """Test create_set_aside with date-based expiration."""
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

                result = api.create_set_aside(
                    account_number="12345",
                    amount=1000,
                    expire_type="Date",
                    expire_date="2026-12-31",
                )

                mock_post.assert_called_once()
                request_json = mock_post.call_args[1]["json"]

                assert request_json["expirationTypeId"] == 1  # Date type
                assert request_json["expirationValue"] == "2026-12-31"

    def test_create_set_aside_no_sync(self):
        """Test create_set_aside with sync=False."""
        with patch.object(EclipseAPI, "login"), patch.object(
            EclipseAPI, "get_internal_account_id", return_value=123
        ), patch.object(EclipseAPI, "_get_auth_header", return_value={}):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch("requests.post") as mock_post, patch.object(
                api, "_maybe_wait_for_analytics"
            ) as mock_wait:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1}
                mock_post.return_value = mock_response

                result = api.create_set_aside(
                    account_number="12345", amount=1000, sync=False
                )

                # Verify _maybe_wait_for_analytics was called with False
                mock_wait.assert_called_once_with(False)
