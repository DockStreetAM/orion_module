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


def _eclipse_v1():
    """Construct an EclipseV1 with auth/login patched out for unit tests."""
    with patch.object(EclipseV1, "login"):
        api = EclipseV1(usr="test", pwd="pass")
    api.eclipse_token = "test-token"
    return api


def _mock_get(records):
    """Return a requests.get mock yielding the given JSON records.

    Patching ``requests.get`` works for GET methods because ``api_request`` resolves
    ``req_func`` at call time (it is not bound as a default argument).
    """
    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = records
    return Mock(return_value=mock_response)


V1_BASE = "https://api.orioneclipse.com/v1"


class TestEclipseV1NewGetEndpoints:
    """URL/params coverage for the new EclipseV1 GET methods (PRD 2.1.0)."""

    def test_get_taxlots(self):
        api = _eclipse_v1()
        mock_get = _mock_get([{"lot": 1}])
        with patch("requests.get", mock_get):
            result = api.get_taxlots(987)
        assert result == [{"lot": 1}]
        assert mock_get.call_args.args[0] == f"{V1_BASE}/holding/holdings/987/taxlots"

    def test_get_raise_cash_methods(self):
        api = _eclipse_v1()
        mock_get = _mock_get([{"id": 1}])
        with patch("requests.get", mock_get):
            api.get_raise_cash_methods()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/tradetool/raisecash/calculation_methods"

    def test_get_spend_cash_methods(self):
        api = _eclipse_v1()
        mock_get = _mock_get([{"id": 1}])
        with patch("requests.get", mock_get):
            api.get_spend_cash_methods()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/tradetool/spendcash/calculation_methods"

    def test_get_model_nodes(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_nodes(55)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/55/Model/nodes"

    def test_get_model_portfolios(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_portfolios(55)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/55/portfolios"

    def test_get_model_pending(self):
        api = _eclipse_v1()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_model_pending(55)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/55/pending"

    def test_get_model_analysis(self):
        api = _eclipse_v1()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_model_analysis(55, asset_type="class")
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/55/modelAnalysis"
        assert mock_get.call_args.kwargs["params"] == {
            "assetType": "class",
            "isIncludeTradeBlockAccount": 0,
            "isExcludeAsset": 0,
        }

    def test_get_model_analysis_default_asset_type(self):
        api = _eclipse_v1()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_model_analysis(55)
        assert mock_get.call_args.kwargs["params"]["assetType"] == "securityset"

    def test_get_model_status(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_status()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/modelStatus"

    def test_get_model_types(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_types()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/modelTypes"

    def test_get_submodels_no_filters(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_submodels()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/submodels"
        assert mock_get.call_args.kwargs["params"] == {}

    def test_get_submodels_with_filters(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_submodels(model_type="A", search="growth")
        assert mock_get.call_args.kwargs["params"] == {"modelType": "A", "name": "growth"}

    def test_get_out_of_tolerance_accounts(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_out_of_tolerance_accounts(10, 20, asset_type="category")
        assert mock_get.call_args.args[0] == f"{V1_BASE}/account/accounts/10/outOfTolerance/20"
        assert mock_get.call_args.kwargs["params"] == {"assetType": "category"}

    def test_get_security_set_details(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_security_set_details()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/security/securityset/detail"

    def test_get_security_set_summary(self):
        api = _eclipse_v1()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_security_set_summary(42)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/security/securityset/42"

    def test_get_account_simple(self):
        api = _eclipse_v1()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_account_simple(123)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/account/accounts/simple/123"

    def test_get_account_holdings_detail(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_account_holdings_detail(123)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/account/accounts/123/holdings"

    def test_get_portfolio_holdings_detail(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_portfolio_holdings_detail(77)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/portfolio/portfolios/77/holdings"

    def test_get_trades_no_filters(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trades()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/tradeorder/trades"
        assert mock_get.call_args.kwargs["params"] == {}

    def test_get_trades_with_filters(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trades(portfolio_id=5, top=10, is_pending=True)
        assert mock_get.call_args.kwargs["params"] == {
            "portfolioId": 5,
            "$top": 10,
            "isPending": "true",
        }


class TestEclipseV1ParamAdditions:
    """Coverage for params added in-place to existing EclipseV1 methods."""

    def test_get_portfolio_accounts_full(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_portfolio_accounts(9)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/portfolio/portfolios/9/accounts"

    def test_get_portfolio_accounts_simple(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_portfolio_accounts(9, simple=True)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/portfolio/portfolios/9/accounts/simple"

    def test_get_all_models_no_params(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_all_models()
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models"
        assert mock_get.call_args.kwargs["params"] == {}

    def test_get_all_models_with_params(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_all_models(name="Core", top=5)
        assert mock_get.call_args.kwargs["params"] == {"name": "Core", "$top": 5}

    def test_get_all_portfolios_default_unchanged(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_all_portfolios()
        # default behavior unchanged: includevalue=true, no $top
        assert mock_get.call_args.kwargs["params"] == {"includevalue": "true"}

    def test_get_all_portfolios_with_top(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_all_portfolios(include_value=False, top=25)
        assert mock_get.call_args.kwargs["params"] == {"includevalue": "false", "$top": 25}

    def test_get_model_allocations_default_aggregate(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_allocations(3)
        assert mock_get.call_args.args[0] == f"{V1_BASE}/modeling/models/3/allocations"
        assert mock_get.call_args.kwargs["params"] == {"aggregateAllocations": "true"}

    def test_get_model_allocations_no_aggregate(self):
        api = _eclipse_v1()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_allocations(3, aggregate=False)
        assert mock_get.call_args.kwargs["params"] == {"aggregateAllocations": "false"}

    def test_get_trade_instances_normalize_false_returns_raw(self):
        api = _eclipse_v1()
        raw = [{"tradeInstanceType": 1, "tradeInstanceSubType": 2}]
        mock_get = _mock_get(raw)
        with patch("requests.get", mock_get):
            result = api.get_trade_instances("2026-01-01", "2026-01-31", normalize=False)
        # Raw IDs preserved, not mapped to friendly names
        assert result == raw
        assert result[0]["tradeInstanceType"] == 1

    def test_get_trade_instances_normalize_true_maps_names(self):
        api = _eclipse_v1()
        raw = [{"tradeInstanceType": 1, "tradeInstanceSubType": 2}]
        mock_get = _mock_get(raw)
        with patch("requests.get", mock_get):
            result = api.get_trade_instances("2026-01-01", "2026-01-31")
        # Default normalize=True maps IDs to strings (or None if unmapped)
        assert result[0]["tradeInstanceType"] != 1


class TestEclipseV1TradeGenPreview:
    """Trade-gen POSTs default to preview (isViewOnly=True, sync=False)."""

    def test_get_tlh_securities_omits_none_ids(self):
        api = _eclipse_v1()
        mock_post = _mock_post([])
        with patch("requests.post", mock_post):
            api.get_tlh_securities(portfolio_ids=[1, 2])
        assert mock_post.call_args.args[0] == (f"{V1_BASE}/tradetool/taxLossHarvesting/securities")
        assert mock_post.call_args.kwargs["json"] == {"portfolioIds": [1, 2]}

    def test_check_tlh_gain_loss(self):
        api = _eclipse_v1()
        mock_post = _mock_post({})
        with patch("requests.post", mock_post):
            api.check_tlh_gain_loss(account_ids=[7])
        assert mock_post.call_args.args[0] == (
            f"{V1_BASE}/tradetool/taxLossHarvesting/action/checkGainLoss"
        )
        assert mock_post.call_args.kwargs["json"] == {"accountIds": [7]}

    def test_tlh_trade_preview_defaults(self):
        api = _eclipse_v1()
        mock_post = _mock_post({"instanceId": 1})
        with (
            patch("requests.post", mock_post),
            patch.object(EclipseV1, "_maybe_wait_for_analytics") as mock_wait,
        ):
            api.tlh_trade(portfolio_ids=[1])
        assert mock_post.call_args.args[0] == (
            f"{V1_BASE}/tradetool/taxLossHarvesting/action/generateTrade"
        )
        body = mock_post.call_args.kwargs["json"]
        assert body["isViewOnly"] is True
        assert body["portfolioIds"] == [1]
        # sync defaults False -> wait called with False (no-op)
        mock_wait.assert_called_once_with(False)

    def test_rebalance_trade_preview_defaults(self):
        api = _eclipse_v1()
        mock_post = _mock_post({"instanceId": 1})
        with (
            patch("requests.post", mock_post),
            patch.object(EclipseV1, "_maybe_wait_for_analytics") as mock_wait,
        ):
            api.rebalance_trade(portfolio_ids=[1, 2])
        assert mock_post.call_args.args[0] == (
            f"{V1_BASE}/tradetool/rebalancer/action/generatetrade"
        )
        body = mock_post.call_args.kwargs["json"]
        assert body["isViewOnly"] is True
        assert body["isExcelImport"] is False
        assert body["minimumTradeAmount"] == {"amount": 0, "type": "$"}
        assert body["allowShortTermGain"] is None
        assert body["priorityRanking"] == []
        assert body["portfolioIds"] == [1, 2]
        assert "accountIds" not in body
        mock_wait.assert_called_once_with(False)

    def test_spend_cash_trade_extra_params_only_when_set(self):
        api = _eclipse_v1()
        mock_post = _mock_post({"instanceId": 1})
        with (
            patch("requests.post", mock_post),
            patch.object(EclipseV1, "_maybe_wait_for_analytics"),
        ):
            api.spend_cash_trade([1])
        body = mock_post.call_args.kwargs["json"]
        assert "selectedMethodId" not in body
        assert "spendFullAmount" not in body
        assert "filterType" not in body

    def test_spend_cash_trade_extra_params_present(self):
        api = _eclipse_v1()
        mock_post = _mock_post({"instanceId": 1})
        with (
            patch("requests.post", mock_post),
            patch.object(EclipseV1, "_maybe_wait_for_analytics"),
        ):
            api.spend_cash_trade([1], selected_method_id=3, spend_full_amount=True, filter_type="X")
        body = mock_post.call_args.kwargs["json"]
        assert body["selectedMethodId"] == 3
        assert body["spendFullAmount"] is True
        assert body["filterType"] == "X"


V2_BASE = "https://api.orioneclipse.com/api/v2"


class TestEclipseV2ReadEndpoints:
    """URL/params coverage for the v2-only read methods (coverage batch 1).

    Patching requests.get works because api_request resolves req_func at call time.
    """

    # --- Tactical ---

    def test_tactical_portfolio_summary(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_tactical_portfolio_summary(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Tactical/PortfolioSummary/7"

    def test_tactical_account_cash_detail(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_tactical_account_cash_detail(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Tactical/AccountAndCashDetail/7"

    def test_tactical_model_analyzer_params(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_tactical_model_analyzer(7, account_id=3, aggregate_alternates=True)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Tactical/ModelAnalyzer/7"
        assert mock_get.call_args.kwargs["params"] == {
            "accountId": 3,
            "aggregateAlternates": "true",
        }

    def test_tactical_model_analyzer_no_params(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_tactical_model_analyzer(7)
        assert mock_get.call_args.kwargs["params"] == {}

    def test_tactical_tax_lots(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_tactical_tax_lots(7, account_id=9)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Tactical/TaxLots/7"
        assert mock_get.call_args.kwargs["params"] == {"accountId": 9}

    def test_tactical_trades(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_tactical_trades(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Tactical/Trades/7"

    def test_tactical_restricted_securities(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_tactical_restricted_securities(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Tactical/RestrictedSecurities/7"

    # --- ESG ---

    def test_esg_themes(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_esg_themes()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/ESG/Themes"

    def test_esg_assignments(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_esg_assignments()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/ESG/Assignments"

    def test_esg_restrictions_for_portfolio(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_esg_restrictions_for_portfolio(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/ESG/ESGRestrictionsForPortfolio"
        assert mock_get.call_args.kwargs["params"] == {"portfolioId": 7}

    # --- Trading blocks ---

    def test_get_trade_blocks_filters(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trade_blocks(has_quodd=True, registration_status="REGISTERED", get_adv=False)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/Blocks"
        assert mock_get.call_args.kwargs["params"] == {
            "hasQuodd": "true",
            "registrationStatus": "REGISTERED",
            "getAdv": "false",
        }

    def test_get_trade_blocks_grid(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trade_blocks_grid([1, 2, 3])
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/Blocks/BlocksGrid"
        assert mock_get.call_args.kwargs["params"] == {"blockIds": [1, 2, 3]}

    def test_get_trade_block_fix_messages(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trade_block_fix_messages(55)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/Blocks/55/FixMessages"

    # --- Dashboard ---

    def test_get_dashboards(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_dashboards(user_id=4, team_id=2)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Dashboard"
        assert mock_get.call_args.kwargs["params"] == {"userId": 4, "teamId": 2}

    def test_get_dashboard(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_dashboard(12)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Dashboard/12"

    def test_get_account_dashboard(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_account_dashboard()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Dashboard/AccountDashboard"

    def test_get_dashboard_fields(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_dashboard_fields()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Dashboard/Fields"

    def test_get_analytics_run_history(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_analytics_run_history()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Dashboard/AnalyticsRunHistory"

    # --- Astro ---

    def test_get_astro_templates(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_astro_templates(al_client_id=99)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Astro/Templates"
        assert mock_get.call_args.kwargs["params"] == {"alClientId": 99}

    def test_get_astro_all_templates(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_astro_all_templates()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Astro/AllTemplates"

    # --- Optimization ---

    def test_get_optimization_summaries(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_optimization_summaries(start_date="2026-01-01", end_date="2026-01-31")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/summaries"
        assert mock_get.call_args.kwargs["params"] == {
            "startDate": "2026-01-01",
            "endDate": "2026-01-31",
        }

    def test_get_optimization_batch_summary_defaults(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_optimization_batch_summary()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/Summary/Batch"
        assert mock_get.call_args.kwargs["params"] == {}

    def test_get_optimization_batch_status(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_optimization_batch_status("nightly-2026-01-15")
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Optimization/Status/Batch/nightly-2026-01-15"
        )

    # --- Asset classification + analytics config ---

    def test_get_asset_classification_groups(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_asset_classification_groups()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/AssetClassification/ClassificationGroups"

    def test_get_asset_classification_methods(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_asset_classification_methods()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/AssetClassification/ClassificationMethods"

    def test_get_analytics_run_config(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_analytics_run_config()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Analytics/RunAnalyticsConfig"

    def test_get_analytics_banner_status(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_analytics_banner_status()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Analytics/BannerSpinner/Status"


class TestEclipseUnifierV2Fallback:
    """The unifier delegates v2-only method names to .v2 (v1 still wins collisions)."""

    def test_v2_only_method_reachable_on_unifier(self):
        from orionapi import Eclipse

        api = Eclipse(eclipse_token="tok")
        # get_tactical_* exists only on v2 -> unifier falls through to v2
        assert api.get_tactical_tax_lots.__self__ is api.v2

    def test_v1_method_still_wins(self):
        from orionapi import Eclipse

        api = Eclipse(eclipse_token="tok")
        # get_account_holdings exists on v1 -> delegated to v1, not v2
        assert api.get_account_holdings.__self__ is api.v1


class TestEclipseV2ReadEndpointsBatch2:
    """URL/params coverage for v2 reads: Trading instances, Optimization, SavedView, Notes."""

    # --- Trading / TradeInstance ---

    def test_trading_instances_filters(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trading_instances(trade_instance_id=5, is_enabled=True, is_deleted=False)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/TradeInstance"
        assert mock_get.call_args.kwargs["params"] == {
            "tradeInstanceId": 5,
            "isEnabled": "true",
            "isDeleted": "false",
        }

    def test_trading_instance_trades(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trading_instance_trades(88)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/TradeInstance/88/Trades"

    def test_trading_instances_for_user(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trading_instances_for_user("2026-01-01", "2026-01-31", offset=0, limit=50)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/TradeInstance/ForUser"
        assert mock_get.call_args.kwargs["params"] == {
            "startDate": "2026-01-01",
            "endDate": "2026-01-31",
            "offset": 0,
            "limit": 50,
        }

    def test_trading_instances_by_date_range(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trading_instances_by_date_range("2026-01-01", "2026-01-31")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/TradeInstance/GetByDateRange"
        assert mock_get.call_args.kwargs["params"] == {
            "startDate": "2026-01-01",
            "endDate": "2026-01-31",
        }

    def test_trading_instances_paginated(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_trading_instances_paginated(portfolio_id=3, skip=0, take=25)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/TradeInstance/Paginated"
        assert mock_get.call_args.kwargs["params"] == {"portfolioId": 3, "skip": 0, "take": 25}

    def test_trading_instances_with_trades(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_trading_instances_with_trades(portfolio_id=3, order_status="Pending")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/TradeInstance/WithTrades"
        assert mock_get.call_args.kwargs["params"] == {"portfolioId": 3, "orderStatus": "Pending"}

    def test_trading_active_batch_jobs(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_trading_active_batch_jobs()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Trading/ActiveBatchJobs"
        assert mock_get.call_args.kwargs["params"] == {}

    # --- Optimization detail ---

    def test_optimization_accounts(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_optimization_accounts("batch-1")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/accounts/batch-1"

    def test_optimization_account_summary(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_optimization_account_summary("batch-1", account_id=9)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/summaries/batch-1"
        assert mock_get.call_args.kwargs["params"] == {"accountId": 9}

    def test_optimization_batch_account_summaries(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_optimization_batch_account_summaries("batch-1")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/summaries/batch/batch-1"

    def test_optimization_account_messages(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_optimization_account_messages("batch-1", account_id=9)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/summaries/batch-1/messages"
        assert mock_get.call_args.kwargs["params"] == {"accountId": 9}

    def test_optimization_log(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_optimization_log(connect_account_id=1, batch_name="b", connect_firm_id=2)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/Log"
        assert mock_get.call_args.kwargs["params"] == {
            "connectAccountId": 1,
            "batchName": "b",
            "connectFirmId": 2,
        }

    def test_optimization_holdings_target(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_optimization_holdings_target(9, batch_name="b")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Optimization/HoldingsTarget/9"
        assert mock_get.call_args.kwargs["params"] == {"batchName": "b"}

    # --- SavedView ---

    def test_saved_views(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_saved_views(4, name="My View")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/SavedView/ViewType/4"
        assert mock_get.call_args.kwargs["params"] == {"name": "My View"}

    def test_saved_views_ranked(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_saved_views_ranked(4, simple_views=True, filter_required=False)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/SavedView/ViewType/4/Rank"
        assert mock_get.call_args.kwargs["params"] == {
            "simpleViews": "true",
            "filterRequired": "false",
        }

    def test_execute_saved_view(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.execute_saved_view(123)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/SavedView/Execute/123"

    # --- Notes ---

    def test_get_notes(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_notes("Portfolio", 7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Notes"
        assert mock_get.call_args.kwargs["params"] == {"relatedType": "Portfolio", "relatedId": 7}

    def test_get_notes_history(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_notes_history("Portfolio", 7, from_date="2026-01-01")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Notes/History"
        assert mock_get.call_args.kwargs["params"] == {
            "relatedType": "Portfolio",
            "relatedId": 7,
            "fromDate": "2026-01-01",
        }

    def test_get_note_related_entities(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_note_related_entities(7, "Portfolio")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Notes/RelatedEntities"
        assert mock_get.call_args.kwargs["params"] == {"entityId": 7, "entityType": "Portfolio"}


class TestEclipseV2ReadEndpointsBatch3:
    """URL/params coverage for v2 account / portfolio / sleeve / preference reads."""

    # --- Account detail ---

    def test_account_cash_details(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_account_cash_details(57)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/Accounts/57/CashDetails"

    def test_account_gain_loss_summary(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_account_gain_loss_summary(57)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/Accounts/57/GainLossSummary"

    def test_account_history_params(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_account_history(57, from_date="2026-01-01", to_date="2026-02-01")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/Accounts/57/History"
        assert mock_get.call_args.kwargs["params"] == {
            "fromDate": "2026-01-01",
            "toDate": "2026-02-01",
        }

    def test_account_model_history(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_account_model_history(57)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/Accounts/57/ModelHistory"
        assert mock_get.call_args.kwargs["params"] == {}

    def test_account_transactions(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_account_transactions(57, start_date="2026-01-01", end_date="2026-02-01")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/Accounts/57/Transactions"
        assert mock_get.call_args.kwargs["params"] == {
            "startDate": "2026-01-01",
            "endDate": "2026-02-01",
        }

    def test_accessible_account_count(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get(3)
        with patch("requests.get", mock_get):
            api.get_accessible_account_count()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/Accounts/AccessibleCount"

    def test_account_by_external(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_account_by_external(11, 22)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/Accounts/byexternal/11/22"

    # --- Astro accounts ---

    def test_astro_accounts(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_astro_accounts(filter="alerts")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/AstroAccounts"
        assert mock_get.call_args.kwargs["params"] == {"filter": "alerts"}

    def test_astro_account_filters(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_astro_account_filters()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Account/AstroAccounts/Filters"

    def test_astro_account_securities_restrictions(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_astro_account_securities_restrictions(57)
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Account/AstroAccounts/57/SecuritiesRestrictions"
        )

    def test_astro_account_investor_preferences(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_astro_account_investor_preferences(57, strategy_name="Core")
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Account/AstroAccounts/57/InvestorPreferences"
        )
        assert mock_get.call_args.kwargs["params"] == {"strategyName": "Core"}

    # --- Portfolio detail ---

    def test_portfolio_allocations(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_portfolio_allocations(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/7/Allocations"

    def test_portfolio_cash_details(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_portfolio_cash_details(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/CashDetails/7"

    def test_portfolio_gain_loss_summary(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_portfolio_gain_loss_summary(7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/7/GainLossSummary"

    def test_portfolio_mac_history(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_portfolio_mac_history(7, from_date="2026-01-01")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/7/MacHistory"
        assert mock_get.call_args.kwargs["params"] == {"fromDate": "2026-01-01"}

    def test_portfolio_auto_rebalance_history(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_portfolio_auto_rebalance_history(7, start_date="2026-01-01")
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Portfolio/Portfolios/7/AutoRebalanceHistory"
        )
        assert mock_get.call_args.kwargs["params"] == {"startDate": "2026-01-01"}

    def test_portfolio_tree(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_portfolio_tree(portfolio_id=7)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/PortfolioTree"
        assert mock_get.call_args.kwargs["params"] == {"portfolioId": 7}

    def test_portfolio_search(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_portfolio_search(search="Smith", include_value=True, limit=10, offset=0)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/GetPortfolioSearch"
        assert mock_get.call_args.kwargs["params"] == {
            "search": "Smith",
            "includeValue": "true",
            "limit": 10,
            "offset": 0,
        }

    def test_accessible_portfolio_count(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get(5)
        with patch("requests.get", mock_get):
            api.get_accessible_portfolio_count()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/AccessibleCount"

    def test_user_portfolio_ids(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_user_portfolio_ids()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Portfolios/GetUserPortfolioIds"

    # --- Sleeves ---

    def test_sleeve_allocations(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_sleeve_allocations(57)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Sleeves/57/Allocations"

    def test_sleeve_strategies(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_sleeve_strategies()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Portfolio/Sleeves/SleeveStrategies"

    def test_sleeve_contribution_methods(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_sleeve_contribution_methods()
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Portfolio/Sleeves/SleeveContributionMethods"
        )

    def test_sleeve_distribution_methods(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_sleeve_distribution_methods()
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Portfolio/Sleeves/SleeveDistributionMethods"
        )

    # --- Preference ---

    def test_get_preference(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_preference("AllowWashSales")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Preference/Preference/GetPreference"
        assert mock_get.call_args.kwargs["params"] == {"preferenceName": "AllowWashSales"}


class TestEclipseV2ReadEndpointsBatch4:
    """URL/params coverage for v2 model / modeling / security / lookup reads."""

    # --- Model / Modeling ---

    def test_models_v2_filters(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_models_v2(search="Core", name="C", model_id=5)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Model/GetAllModels"
        assert mock_get.call_args.kwargs["params"] == {
            "modelId": 5,
            "search": "Core",
            "name": "C",
        }

    def test_model_types_v2(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_types_v2()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Model/GetModelTypes"

    def test_model_risk_profile(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_model_risk_profile(5, "1Y")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Model/5/RiskProfile/1Y"

    def test_model_sync_oc_firms(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_sync_oc_firms(5)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Model/GetModelSyncToOCFirms"
        assert mock_get.call_args.kwargs["params"] == {"modelId": 5}

    def test_model_levels(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_model_levels(5)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Modeling/Models/5/Levels"

    def test_model_analysis_v2(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_model_analysis_v2(5, asset_type="class", is_include_cost_basis=True)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Modeling/Models/5/ModelAnalysis"
        assert mock_get.call_args.kwargs["params"] == {
            "assetType": "class",
            "isIncludeCostBasis": "true",
        }

    def test_model_aggregate_analysis(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_model_aggregate_analysis(5)
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Modeling/Models/5/ModelAnalysis/ModelAggregate"
        )
        assert mock_get.call_args.kwargs["params"] == {}

    def test_astro_models(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_astro_models()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Modeling/Models/Astro"

    def test_strategist_models(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_strategist_models()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Modeling/Models/GetStrategistModels"

    def test_stress_test_scenarios(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_stress_test_scenarios()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Modeling/Models/StressTestScenarios"

    def test_hidden_levers_user_status(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get({})
        with patch("requests.get", mock_get):
            api.get_hidden_levers_user_status("a@b.com")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Modeling/Models/UserStatus"
        assert mock_get.call_args.kwargs["params"] == {"email": "a@b.com"}

    # --- Security / SecuritySet ---

    def test_get_securities(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_securities(security_id=42, is_cached=True)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Security/GetSecurities"
        assert mock_get.call_args.kwargs["params"] == {"securityId": 42, "isCached": "true"}

    def test_security_sets_v2(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_security_sets_v2(security_set_id=9)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/SecuritySet/GetSecuritySets"
        assert mock_get.call_args.kwargs["params"] == {"securitySetId": 9}

    def test_security_set_history(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_security_set_history(9, from_date="2026-01-01")
        assert mock_get.call_args.args[0] == f"{V2_BASE}/SecuritySet/9/History"
        assert mock_get.call_args.kwargs["params"] == {"fromDate": "2026-01-01"}

    def test_security_set_detail_history(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_security_set_detail_history(9)
        assert mock_get.call_args.args[0] == f"{V2_BASE}/SecuritySet/9/DetailHistory"

    # --- Lookup ---

    def test_hidden_levers_durations(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_hidden_levers_durations()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Lookup/HiddenLeversDurations"

    def test_sma_account_type_restrictions_all(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_sma_account_type_restrictions()
        assert mock_get.call_args.args[0] == f"{V2_BASE}/Lookup/SmaAccountTypeRestrictions"

    def test_sma_account_type_restrictions_category(self):
        api = _eclipse_for_set_asides()
        mock_get = _mock_get([])
        with patch("requests.get", mock_get):
            api.get_sma_account_type_restrictions(category="IRA")
        assert mock_get.call_args.args[0] == (
            f"{V2_BASE}/Lookup/SmaAccountTypeRestrictions/Category/IRA"
        )
