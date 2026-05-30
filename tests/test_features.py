"""Feature tests for orionapi update operations and analytics.

Tests for medium-priority features identified in coverage analysis.
"""

import time
from unittest.mock import Mock, patch

import pytest

from orionapi import EclipseAPI, EclipseV1, EclipseV2, OrionAPI


class TestOrionUpdateOperations:
    """Test OrionAPI update operations."""

    def test_update_client(self):
        """Test updating a client/household."""
        with (
            patch.object(OrionAPI, "login"),
            patch.object(OrionAPI, "_get_auth_header", return_value={}),
            patch.object(
                OrionAPI, "_translate_custom_fields", return_value={"name": "Updated Name"}
            ),
        ):
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
        with (
            patch.object(OrionAPI, "login"),
            patch.object(OrionAPI, "_get_auth_header", return_value={}),
            patch.object(
                OrionAPI, "_translate_custom_fields", return_value={"name": "Updated Registration"}
            ),
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
        with (
            patch.object(OrionAPI, "login"),
            patch.object(OrionAPI, "_get_auth_header", return_value={}),
            patch.object(OrionAPI, "_translate_custom_fields", return_value={"accountType": "IRA"}),
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


# EclipseV1 doesn't have update operations yet, removed invalid test


class TestEclipseAnalytics:
    """Test Eclipse analytics methods."""

    def test_get_analytics_status_running(self):
        """Test getting analytics status when running."""
        with patch.object(EclipseV1, "login"):
            api = EclipseV1(usr="test", pwd="pass")

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
        with patch.object(EclipseV1, "login"):
            api = EclipseV1(usr="test", pwd="pass")

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
        with patch.object(EclipseV1, "login"):
            api = EclipseV1(usr="test", pwd="pass")

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
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with patch.object(
                api, "get_analytics_status", return_value={"isAnalysisRunning": False}
            ):
                start = time.time()
                result = api.wait_for_analytics(poll_interval=0.1)
                duration = time.time() - start

                assert result is True
                assert duration < 0.5  # Should return immediately

    def test_wait_for_analytics_polls_until_complete(self):
        """Test wait_for_analytics polls until complete."""
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
        ):
            api = EclipseV1(usr="test", pwd="pass")

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
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with patch.object(
                api, "get_analytics_status", return_value={"isAnalysisRunning": True}
            ):  # Never completes
                with pytest.raises(TimeoutError, match="did not complete within"):
                    api.wait_for_analytics(poll_interval=0.1, timeout=0.3)

    def test_maybe_wait_for_analytics_when_sync_true(self):
        """Test _maybe_wait_for_analytics waits when sync=True."""
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with patch.object(api, "wait_for_analytics", return_value=True) as mock_wait:
                api._maybe_wait_for_analytics(sync=True)

                mock_wait.assert_called_once()

    def test_maybe_wait_for_analytics_when_sync_false(self):
        """Test _maybe_wait_for_analytics skips when sync=False."""
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with patch.object(api, "wait_for_analytics", return_value=True) as mock_wait:
                api._maybe_wait_for_analytics(sync=False)

                mock_wait.assert_not_called()


class TestCreateSetAsideExtended:
    """Extended tests for create_set_aside with various configurations."""

    def test_create_set_aside_with_description(self):
        """Test create_set_aside with description."""
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "get_internal_account_id", return_value=123),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
            patch.object(EclipseV1, "_maybe_wait_for_analytics"),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1, "description": "Emergency Fund"}
                mock_post.return_value = mock_response

                api.create_set_aside(
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
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "get_internal_account_id", return_value=123),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
            patch.object(EclipseV1, "_maybe_wait_for_analytics"),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1}
                mock_post.return_value = mock_response

                api.create_set_aside(
                    account_number="12345",
                    amount=10,
                    cash_type="%",  # Percentage
                )

                mock_post.assert_called_once()
                request_json = mock_post.call_args[1]["json"]

                assert request_json["cashAmountTypeId"] == 2  # Percentage type ID

    def test_create_set_aside_date_expiration(self):
        """Test create_set_aside with date-based expiration."""
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "get_internal_account_id", return_value=123),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
            patch.object(EclipseV1, "_maybe_wait_for_analytics"),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with patch("requests.post") as mock_post:
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1}
                mock_post.return_value = mock_response

                api.create_set_aside(
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
        with (
            patch.object(EclipseV1, "login"),
            patch.object(EclipseV1, "get_internal_account_id", return_value=123),
            patch.object(EclipseV1, "_get_auth_header", return_value={}),
        ):
            api = EclipseV1(usr="test", pwd="pass")

            with (
                patch("requests.post") as mock_post,
                patch.object(api, "_maybe_wait_for_analytics") as mock_wait,
            ):
                mock_response = Mock()
                mock_response.ok = True
                mock_response.json.return_value = {"id": 1}
                mock_post.return_value = mock_response

                api.create_set_aside(account_number="12345", amount=1000, sync=False)

                # Verify _maybe_wait_for_analytics was called with False
                mock_wait.assert_called_once_with(False)


# A realistic v2 AccountSetAsideCashResponseDto record (from live response).
SAMPLE_SET_ASIDE = {
    "id": 1723,
    "accountId": 1114,
    "accountNumber": "08197200",
    "setAsideCashAmount": 15500.0,
    "setAsideCashAmountType": "Dollar",
    "cashAmountTypeId": 1,
    "cashAmountType": "$",
    "isActive": True,
    "expirationValue": None,
    "expirationTypeId": 3,
    "expirationType": "None",
    "startDate": "2026-03-05T00:00:00",
    "description": "1 month of beneficiary distributions, paid monthly",
}


def _eclipse_for_set_asides():
    """Construct an EclipseV2 with auth/login patched out for unit tests."""
    with patch.object(EclipseV2, "login"):
        api = EclipseV2(usr="test", pwd="pass")
    # Provide a token so the real _get_auth_header succeeds during requests.
    api.eclipse_token = "test-token"
    return api


def _mock_post(records):
    """Return a requests.post mock yielding the given JSON records."""
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = records
    mock_post = Mock(return_value=mock_response)
    return mock_post


class TestGetSetAsides:
    """Tests for the unified get_set_asides method (v2 batch endpoint)."""

    def test_per_account_normalizes_and_posts_account_id(self):
        """Per-account call posts [internal_id] to the v2 endpoint and normalizes."""
        api = _eclipse_for_set_asides()
        with patch.object(api, "get_internal_account_id", return_value=123):
            mock_post = _mock_post([dict(SAMPLE_SET_ASIDE)])
            with patch("requests.post", mock_post):
                result = api.get_set_asides("08197200")

        # POST body is the resolved internal account id list
        assert mock_post.call_args.kwargs["json"] == [123]
        # URL targets the v2 host-root surface, not /v1
        assert mock_post.call_args.args[0] == (
            "https://api.orioneclipse.com/api/v2/Account/Accounts/SetAsideCashSettings"
        )

        rec = result[0]
        # Normalized keys
        assert rec["set_aside_id"] == 1723
        assert rec["amount"] == 15500.0
        assert rec["active"] is True
        assert rec["account_number"] == "08197200"
        assert rec["start_date"] == "2026-03-05T00:00:00"
        # Original raw keys preserved (augmentation, not replacement)
        assert rec["id"] == 1723
        assert rec["setAsideCashAmount"] == 15500.0

    def test_firmwide_posts_all_account_ids(self):
        """Firm-wide call (no account_id) posts all account ids from get_all_accounts."""
        api = _eclipse_for_set_asides()
        with patch.object(api, "get_all_accounts", return_value=[{"id": 1}, {"id": 2}]):
            mock_post = _mock_post([dict(SAMPLE_SET_ASIDE)])
            with patch("requests.post", mock_post):
                result = api.get_set_asides()

        assert mock_post.call_args.kwargs["json"] == [1, 2]
        assert result[0]["set_aside_id"] == 1723

    def test_active_only_filters_inactive(self):
        """active_only=True drops records whose isActive is False."""
        api = _eclipse_for_set_asides()
        inactive = {**SAMPLE_SET_ASIDE, "id": 9, "isActive": False}
        with patch.object(api, "get_internal_account_id", return_value=123):
            mock_post = _mock_post([dict(SAMPLE_SET_ASIDE), inactive])
            with patch("requests.post", mock_post):
                active = api.get_set_asides("08197200", active_only=True)
                all_records = api.get_set_asides("08197200")

        assert [r["set_aside_id"] for r in active] == [1723]
        assert len(all_records) == 2

    def test_end_date_mapping(self):
        """end_date is the expirationValue for date-based expirations, else None."""
        api = _eclipse_for_set_asides()
        date_based = {
            **SAMPLE_SET_ASIDE,
            "id": 5,
            "expirationTypeId": 1,
            "expirationValue": "2026-12-31",
        }
        with patch.object(api, "get_internal_account_id", return_value=123):
            mock_post = _mock_post([date_based, dict(SAMPLE_SET_ASIDE)])
            with patch("requests.post", mock_post):
                result = api.get_set_asides("08197200")

        by_id = {r["set_aside_id"]: r for r in result}
        assert by_id[5]["end_date"] == "2026-12-31"
        assert by_id[1723]["end_date"] is None


class TestEclipseRequest:
    """Tests for the generic eclipse_request escape hatch."""

    def test_v1_get_default(self):
        """version='v1' targets the /v1 base with a GET by default."""
        api = _eclipse_for_set_asides()
        mock_get = Mock(return_value=Mock(ok=True, json=lambda: {"ok": True}))
        with patch("requests.get", mock_get):
            result = api.eclipse_request("account/accounts/simple")
        assert result == {"ok": True}
        assert mock_get.call_args.args[0] == (
            "https://api.orioneclipse.com/v1/account/accounts/simple"
        )

    def test_v2_post_with_body(self):
        """version='v2' targets the /api/v2 host-root base; method/body pass through."""
        api = _eclipse_for_set_asides()
        mock_post = _mock_post([{"id": 1}])
        with patch("requests.post", mock_post):
            result = api.eclipse_request(
                "/Account/Accounts/SetAsideCashSettings", version="v2", method="post", json=[1]
            )
        assert result == [{"id": 1}]
        assert mock_post.call_args.args[0] == (
            "https://api.orioneclipse.com/api/v2/Account/Accounts/SetAsideCashSettings"
        )
        assert mock_post.call_args.kwargs["json"] == [1]

    def test_leading_slash_optional(self):
        """Paths with or without a leading slash resolve identically."""
        api = _eclipse_for_set_asides()
        mock_get = Mock(return_value=Mock(ok=True, json=lambda: {}))
        with patch("requests.get", mock_get):
            api.eclipse_request("Account/Accounts", version="v2")
            api.eclipse_request("/Account/Accounts", version="v2")
        urls = {call.args[0] for call in mock_get.call_args_list}
        assert urls == {"https://api.orioneclipse.com/api/v2/Account/Accounts"}

    def test_invalid_version_and_method_raise(self):
        """Unknown version or HTTP method raises ValueError."""
        api = _eclipse_for_set_asides()
        with pytest.raises(ValueError, match="version must be"):
            api.eclipse_request("x", version="v3")
        with pytest.raises(ValueError, match="method must be"):
            api.eclipse_request("x", method="patch")


class TestEclipseUnifierAndAlias:
    """The Eclipse unifier composes v1/v2; EclipseAPI is a deprecated alias."""

    def test_unifier_shares_token_and_exposes_subclients(self):
        """Eclipse injects its token into .v1 / .v2 without re-logging in."""
        from orionapi import Eclipse

        api = Eclipse(eclipse_token="tok")
        assert api.eclipse_token == "tok"
        assert api.v1.eclipse_token == "tok"
        assert api.v2.eclipse_token == "tok"
        assert isinstance(api.v1, EclipseV1)
        assert isinstance(api.v2, EclipseV2)

    def test_unifier_delegates_v1_and_prefers_v2_for_set_asides(self):
        """Unknown attrs delegate to v1; get_set_asides is overridden to use v2."""
        from orionapi import Eclipse

        api = Eclipse(eclipse_token="tok")
        # delegated v1 method is bound to the v1 sub-client
        assert api.create_set_aside.__self__ is api.v1
        # get_set_asides is the unifier's own override (routes to v2)
        assert api.get_set_asides.__self__ is api

    def test_eclipse_api_alias_warns_and_constructs(self):
        """EclipseAPI emits DeprecationWarning and still builds the unifier."""
        with pytest.warns(DeprecationWarning, match="EclipseAPI is deprecated"):
            api = EclipseAPI(eclipse_token="tok")
        assert isinstance(api, EclipseAPI)
        assert api.eclipse_token == "tok"
        assert api.v1.eclipse_token == "tok"
