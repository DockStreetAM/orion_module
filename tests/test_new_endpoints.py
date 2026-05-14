"""Unit tests for newly added API endpoints.

Tests for OrionAPI and EclipseAPI methods added in v1.4.0.
"""

from unittest.mock import Mock, patch

import pytest

from orionapi import EclipseAPI, OrionAPI, OrionAPIError


class TestOrionAssets:
    """Test OrionAPI asset methods."""

    def test_get_assets(self):
        """Test getting assets for an account."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = [
                    {"id": 1, "symbol": "AAPL", "value": 10000},
                    {"id": 2, "symbol": "MSFT", "value": 15000},
                ]
                mock_api_request.return_value = mock_response

                result = api.get_assets(account_id=123, has_value=True)

                mock_api_request.assert_called_once()
                assert len(result) == 2
                assert result[0]["symbol"] == "AAPL"

    def test_get_assets_invalid_account_id(self):
        """Test get_assets with invalid account ID."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="account_id must be a positive integer"):
                api.get_assets(account_id=0)

            with pytest.raises(ValueError, match="account_id must be a positive integer"):
                api.get_assets(account_id=-1)

    def test_search_assets(self):
        """Test searching for assets."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = [
                    {"id": 1, "symbol": "AAPL", "name": "Apple Inc."},
                ]
                mock_api_request.return_value = mock_response

                result = api.search_assets(search_term="AAPL", top=5)

                mock_api_request.assert_called_once()
                assert len(result) == 1
                assert result[0]["symbol"] == "AAPL"

    def test_search_assets_invalid_params(self):
        """Test search_assets with invalid parameters."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="search_term must be a non-empty string"):
                api.search_assets(search_term="")

            with pytest.raises(ValueError, match="top must be a positive integer"):
                api.search_assets(search_term="AAPL", top=0)


class TestOrionBilling:
    """Test OrionAPI billing methods."""

    def test_get_fee_schedules(self):
        """Test getting fee schedules."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = [
                    {"id": 1, "name": "Standard Fee Schedule", "rate": 1.0},
                ]
                mock_api_request.return_value = mock_response

                result = api.get_fee_schedules()

                mock_api_request.assert_called_once()
                assert len(result) == 1
                assert result[0]["name"] == "Standard Fee Schedule"

    def test_get_account_billing(self):
        """Test getting billing for an account."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "id": 123,
                    "feeScheduleId": 1,
                    "billingMethod": "arrears",
                }
                mock_api_request.return_value = mock_response

                result = api.get_account_billing(account_id=123)

                mock_api_request.assert_called_once()
                assert result["id"] == 123
                assert result["feeScheduleId"] == 1

    def test_get_account_billing_invalid_id(self):
        """Test get_account_billing with invalid ID."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="account_id must be a positive integer"):
                api.get_account_billing(account_id=-1)

    def test_get_billing_household_summary(self):
        """Test getting billing summary for a household."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "householdId": 456,
                    "totalFees": 5000.0,
                    "accounts": 3,
                }
                mock_api_request.return_value = mock_response

                result = api.get_billing_household_summary(household_id=456)

                mock_api_request.assert_called_once()
                assert result["householdId"] == 456
                assert result["totalFees"] == 5000.0


class TestOrionReporting:
    """Test OrionAPI reporting methods."""

    def test_get_performance_data_account(self):
        """Test getting performance data for an account."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "returns": {"ytd": 5.5, "oneYear": 12.3},
                    "benchmarks": {},
                }
                mock_api_request.return_value = mock_response

                result = api.get_performance_data(
                    entity_id=123,
                    start_date="2024-01-01",
                    end_date="2024-12-31",
                    entity_type="account",
                )

                mock_api_request.assert_called_once()
                assert "returns" in result
                assert result["returns"]["ytd"] == 5.5

    def test_get_performance_data_client(self):
        """Test getting performance data for a client."""
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {"returns": {}}
                mock_api_request.return_value = mock_response

                api.get_performance_data(
                    entity_id=456,
                    start_date="2024-01-01",
                    end_date="2024-12-31",
                    entity_type="client",
                )

                mock_api_request.assert_called_once()
                # Verify the endpoint includes /Clients/
                call_args = mock_api_request.call_args[0][0]
                assert "/Portfolio/Clients/" in call_args

    def test_get_performance_data_invalid_entity_type(self):
        """Test get_performance_data with invalid entity type."""
        with patch.object(OrionAPI, "login"):
            api = OrionAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="entity_type must be one of"):
                api.get_performance_data(
                    entity_id=123,
                    start_date="2024-01-01",
                    end_date="2024-12-31",
                    entity_type="invalid",
                )


class TestEclipseTrades:
    """Test EclipseAPI trade methods."""

    def test_get_trade_status(self):
        """Test getting trade status."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "id": 789,
                    "isEnabled": True,
                    "orderQty": 100,
                    "action": {"name": "BUY"},
                }
                mock_api_request.return_value = mock_response

                result = api.get_trade_status(trade_id=789)

                mock_api_request.assert_called_once()
                assert result["id"] == 789
                assert result["action"]["name"] == "BUY"

    def test_get_trade_status_invalid_id(self):
        """Test get_trade_status with invalid ID."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="trade_id must be a positive integer"):
                api.get_trade_status(trade_id=0)

    def test_get_trade_instance(self):
        """Test getting trade instance details."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "id": 4891,
                    "caption": None,
                    "isEnabled": 1,
                    "notes": "Cash needs trade",
                    "orderCount": 5,
                    "executeStatus": "New",
                    "closedOrderCount": 0,
                    "openOrderCount": 5,
                }
                mock_api_request.return_value = mock_response

                result = api.get_trade_instance(instance_id=4891)

                mock_api_request.assert_called_once()
                assert result["id"] == 4891
                assert result["executeStatus"] == "New"
                assert result["orderCount"] == 5

    def test_get_trade_instance_invalid_id(self):
        """Test get_trade_instance with invalid ID."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="instance_id must be a positive integer"):
                api.get_trade_instance(instance_id=0)

    def test_get_trade_instance_logs(self):
        """Test getting trade instance logs."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = [
                    {
                        "id": 7805,
                        "tradeInstanceId": 4891,
                        "description": "cashNeeds",
                        "portfolioId": 226,
                        "portfolioName": "Test Portfolio",
                        "applicationName": "CashNeeds",
                    }
                ]
                mock_api_request.return_value = mock_response

                result = api.get_trade_instance_logs(instance_id=4891)

                mock_api_request.assert_called_once()
                assert isinstance(result, list)
                assert len(result) == 1
                assert result[0]["tradeInstanceId"] == 4891
                assert result[0]["applicationName"] == "CashNeeds"

    def test_get_trade_instance_logs_invalid_id(self):
        """Test get_trade_instance_logs with invalid ID."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="instance_id must be a positive integer"):
                api.get_trade_instance_logs(instance_id=-1)

    def test_get_trade_log_detail(self):
        """Test getting detailed HTML trade log."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                import base64

                # Mock HTML content
                html_content = "<html><body>Trade log details...</body></html>"
                encoded_content = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

                mock_response = Mock()
                mock_response.json.return_value = {
                    "isSuccess": True,
                    "content": encoded_content,
                }
                mock_api_request.return_value = mock_response

                result = api.get_trade_log_detail(log_id=7805)

                mock_api_request.assert_called_once()
                # Verify it called the v2 endpoint
                call_args = mock_api_request.call_args[0][0]
                assert "/v2/Trading/TradeLogById/7805" in call_args

                # Verify HTML was decoded
                assert result == html_content
                assert "<html>" in result

    def test_get_trade_log_detail_invalid_id(self):
        """Test get_trade_log_detail with invalid ID."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="log_id must be a positive integer"):
                api.get_trade_log_detail(log_id=0)

    def test_get_portfolio_trade_instances(self):
        """Test getting trade instances for a portfolio."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = [
                    {
                        "id": 4891,
                        "requestType": "CashNeeds",
                        "executeStatus": "New",
                        "orderCount": 5,
                    },
                    {
                        "id": 4890,
                        "requestType": "SpendCash",
                        "executeStatus": "Complete",
                        "orderCount": 3,
                    },
                ]
                mock_api_request.return_value = mock_response

                result = api.get_portfolio_trade_instances(
                    portfolio_id=226, start_date="2026-01-01", end_date="2026-01-31"
                )

                mock_api_request.assert_called_once()
                call_args = mock_api_request.call_args[0][0]
                assert "/tradeorder/instances/portfolio/226/search" in call_args
                assert "startDate=2026-01-01" in call_args
                assert "endDate=2026-01-31" in call_args

                assert isinstance(result, list)
                assert len(result) == 2
                assert result[0]["id"] == 4891

    def test_get_portfolio_trade_instances_invalid_params(self):
        """Test get_portfolio_trade_instances with invalid parameters."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="portfolio_id must be a positive integer"):
                api.get_portfolio_trade_instances(
                    portfolio_id=0, start_date="2026-01-01", end_date="2026-01-31"
                )

            with pytest.raises(ValueError, match="start_date must be a non-empty string"):
                api.get_portfolio_trade_instances(
                    portfolio_id=226, start_date="", end_date="2026-01-31"
                )

            with pytest.raises(ValueError, match="end_date must be a non-empty string"):
                api.get_portfolio_trade_instances(
                    portfolio_id=226, start_date="2026-01-01", end_date=""
                )


class TestEclipseSecurityPreferences:
    """Test EclipseAPI security preferences methods."""

    def test_get_security_preferences(self):
        """Test getting security preferences."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "levelName": "Portfolio",
                    "recordId": 123,
                    "securityPreferences": [
                        {
                            "id": 1,
                            "symbol": "AAPL",
                            "buyTradeMaxPctBySecurity": 10.0,
                        }
                    ],
                }
                mock_api_request.return_value = mock_response

                result = api.get_security_preferences(portfolio_id=123, security_id=456)

                mock_api_request.assert_called_once()
                assert result["levelName"] == "Portfolio"
                assert len(result["securityPreferences"]) == 1

    def test_get_security_preferences_invalid_params(self):
        """Test get_security_preferences with invalid parameters."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="portfolio_id must be a positive integer"):
                api.get_security_preferences(portfolio_id=0, security_id=1)

            with pytest.raises(ValueError, match="security_id must be a positive integer"):
                api.get_security_preferences(portfolio_id=1, security_id=-1)


class TestEclipseTradeRestrictions:
    """Test EclipseAPI trade restriction methods."""

    def test_set_portfolio_tradeable_block(self):
        """Test blocking portfolio trading."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            # Mock get_portfolio to return current portfolio state
            with patch.object(api, "get_portfolio") as mock_get, patch.object(
                api, "api_request"
            ) as mock_api_request, patch.object(api, "_maybe_wait_for_analytics"):
                mock_get.return_value = {
                    "general": {
                        "portfolioName": "Test Portfolio",
                        "modelId": 1,
                        "sleevePortfolio": False,
                        "doNotTrade": 0,
                        "tags": "test",
                        "teamIds": [1],
                        "primaryTeamId": 1,
                    }
                }

                mock_response = Mock()
                mock_response.json.return_value = {"general": {"doNotTrade": 1}}
                mock_api_request.return_value = mock_response

                result = api.set_portfolio_tradeable(portfolio_id=123, tradeable=False, sync=False)

                assert result["general"]["doNotTrade"] == 1

    def test_set_account_tradeable_block_advisor(self):
        """Test blocking advisor trading for an account."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "get_account_details") as mock_get, patch.object(
                api, "api_request"
            ) as mock_api_request, patch.object(api, "_maybe_wait_for_analytics"):
                mock_get.return_value = {
                    "generalSection": {
                        "accountName": "Test Account",
                        "portfolioId": 1,
                        "doNotTrade": 0,
                        "doNotTradeCustodian": 0,
                    }
                }

                mock_response = Mock()
                mock_response.json.return_value = {"generalSection": {"doNotTrade": 1}}
                mock_api_request.return_value = mock_response

                api.set_account_tradeable(
                    account_id=456, trade_restriction="block_advisor", sync=False
                )

                # Verify the request was made with correct payload
                call_args = mock_api_request.call_args
                payload = call_args[1]["json"]
                assert payload["doNotTrade"] == 1
                assert payload["doNotTradeCustodian"] == 0

    def test_set_account_tradeable_invalid_restriction(self):
        """Test set_account_tradeable with invalid restriction."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with pytest.raises(ValueError, match="trade_restriction must be one of"):
                api.set_account_tradeable(account_id=123, trade_restriction="invalid")


class TestEclipseTradeTools:
    """Test EclipseAPI trade tool methods."""

    def test_spend_cash_trade(self):
        """Test generating Spend Cash trade."""
        with patch.object(EclipseAPI, "login"):
            api = EclipseAPI(usr="test", pwd="pass")

            with patch.object(api, "api_request") as mock_api_request, patch.object(
                api, "_maybe_wait_for_analytics"
            ):
                mock_response = Mock()
                mock_response.json.return_value = {
                    "issues": [],
                    "success": True,
                    "instanceId": 5000,
                }
                mock_api_request.return_value = mock_response

                result = api.spend_cash_trade(
                    portfolio_ids=[123, 456],
                    reason="Test spend cash",
                    is_view_only=True,
                    sync=False,
                )

                # Verify the request was made correctly
                mock_api_request.assert_called_once()
                call_args = mock_api_request.call_args
                assert "/tradetool/spendcash/action/generatetrade" in call_args[0][0]

                payload = call_args[1]["json"]
                assert payload["portfolioIds"] == [123, 456]
                assert payload["reason"] == "Test spend cash"
                assert payload["isViewOnly"] is True

                # Verify response
                assert result["success"] is True
                assert result["instanceId"] == 5000


class TestOrionBillingWorkflow:
    """Test OrionAPI billing workflow methods."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            return OrionAPI(usr="test", pwd="pass")

    def test_get_billing_instances(self):
        """Test listing billing instances."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[{"id": 1}, {"id": 2}]))
            result = api.get_billing_instances(start_date="2026-01-01", end_date="2026-03-31")
            assert len(result) == 2
            call_url = mock.call_args[0][0]
            assert "startDate=2026-01-01" in call_url
            assert "endDate=2026-03-31" in call_url

    def test_get_billing_instances_no_filter(self):
        """Test listing billing instances without filters."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[]))
            api.get_billing_instances()
            call_url = mock.call_args[0][0]
            assert "?" not in call_url

    def test_get_billing_instance(self):
        """Test getting a single billing instance."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"id": 42, "status": "Complete"}))
            result = api.get_billing_instance(instance_id=42)
            assert result["id"] == 42
            assert "/Billing/Instances/42" in mock.call_args[0][0]

    def test_get_billing_instance_invalid_id(self):
        """Test get_billing_instance with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.get_billing_instance(instance_id=0)
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.get_billing_instance(instance_id=-1)

    def test_create_billing_instance_defaults(self):
        """Test creating a billing instance with defaults."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"id": 100}))
            result = api.create_billing_instance()
            assert result["id"] == 100
            payload = mock.call_args[1]["json"]
            assert payload["isMockBill"] is False
            assert payload["runFor"] == "AllHouseholds"
            assert payload["runForAccounts"] == "ActiveAccounts"
            assert payload["billType"] == "Renewal"
            assert payload["includeCashFlow"] is False

    def test_create_billing_instance_forecast(self):
        """Test creating a forecast billing instance."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"id": 101}))
            api.create_billing_instance(
                is_forecast=True,
                nickname="Q1 Forecast",
                keys=[1, 2, 3],
                as_of_date="2026-03-31",
            )
            payload = mock.call_args[1]["json"]
            assert payload["isMockBill"] is True
            assert payload["nickName"] == "Q1 Forecast"
            assert payload["keys"] == [1, 2, 3]
            assert payload["asOfDate"] == "2026-03-31"

    def test_create_billing_instance_invalid_run_for(self):
        """Test create_billing_instance with invalid run_for."""
        api = self._make_api()
        with pytest.raises(ValueError, match="run_for must be one of"):
            api.create_billing_instance(run_for="InvalidScope")

    def test_create_billing_instance_invalid_run_for_accounts(self):
        """Test create_billing_instance with invalid run_for_accounts."""
        api = self._make_api()
        with pytest.raises(ValueError, match="run_for_accounts must be one of"):
            api.create_billing_instance(run_for_accounts="BadFilter")

    def test_create_billing_instance_invalid_bill_type(self):
        """Test create_billing_instance with invalid bill_type."""
        api = self._make_api()
        with pytest.raises(ValueError, match="bill_type must be one of"):
            api.create_billing_instance(bill_type="FakeType")

    def test_create_billing_instance_invalid_keys(self):
        """Test create_billing_instance with invalid keys."""
        api = self._make_api()
        with pytest.raises(ValueError, match="keys must be a list"):
            api.create_billing_instance(keys=42)

    def test_generate_billing(self):
        """Test generating bills for an instance."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"status": "Generated"}))
            result = api.generate_billing(instance_id=42)
            assert result["status"] == "Generated"
            call_url = mock.call_args[0][0]
            assert "/Billing/Instances/42/Action/Generate" in call_url
            assert "lockDown=true" in call_url

    def test_generate_billing_no_lockdown(self):
        """Test generating bills without lock down."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={}))
            api.generate_billing(instance_id=1, lock_down=False)
            call_url = mock.call_args[0][0]
            assert "lockDown=false" in call_url

    def test_generate_billing_invalid_id(self):
        """Test generate_billing with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.generate_billing(instance_id=0)

    def test_complete_billing_instance(self):
        """Test completing a billing instance."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"id": 42, "status": "Complete"}))
            result = api.complete_billing_instance(instance_id=42)
            assert result["status"] == "Complete"
            assert "/Billing/Instances/42/Action/Complete" in mock.call_args[0][0]

    def test_complete_billing_instance_invalid_id(self):
        """Test complete_billing_instance with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.complete_billing_instance(instance_id=-5)

    def test_invalidate_billing_instance(self):
        """Test invalidating a billing instance."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"id": 42, "status": "Invalid"}))
            result = api.invalidate_billing_instance(instance_id=42)
            assert result["status"] == "Invalid"
            assert "/Billing/Instances/42/Action/Invalidate" in mock.call_args[0][0]

    def test_invalidate_billing_instance_invalid_id(self):
        """Test invalidate_billing_instance with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.invalidate_billing_instance(instance_id=0)

    def test_generate_fee_files(self):
        """Test generating fee files."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"success": True}))
            result = api.generate_fee_files(instance_id=42)
            assert result["success"] is True
            payload = mock.call_args[1]["json"]
            assert payload == {"ids": [42]}
            assert "custodianId" not in mock.call_args[0][0]

    def test_generate_fee_files_with_custodian(self):
        """Test generating fee files for a specific custodian."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"success": True}))
            api.generate_fee_files(instance_id=42, custodian_id=7)
            call_url = mock.call_args[0][0]
            assert "custodianId=7" in call_url

    def test_generate_fee_files_invalid_id(self):
        """Test generate_fee_files with invalid IDs."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.generate_fee_files(instance_id=0)

    def test_generate_fee_files_invalid_custodian_id(self):
        """Test generate_fee_files with invalid custodian ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="custodian_id must be a positive integer"):
            api.generate_fee_files(instance_id=1, custodian_id=-1)

    def test_get_fee_files(self):
        """Test getting fee files."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(
                json=Mock(return_value=[{"fileName": "fees.csv", "status": "Ready"}])
            )
            result = api.get_fee_files(instance_id=42)
            assert len(result) == 1
            assert result[0]["fileName"] == "fees.csv"
            assert "/Billing/FeeFile/instance/42" in mock.call_args[0][0]

    def test_get_fee_files_invalid_id(self):
        """Test get_fee_files with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.get_fee_files(instance_id=0)

    def test_get_bills(self):
        """Test getting bills with filters."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[{"id": 1, "amount": 500.0}]))
            result = api.get_bills(instance_id=42, is_valid=True, bill_type="Renewal")
            assert len(result) == 1
            call_url = mock.call_args[0][0]
            assert "instanceId=42" in call_url
            assert "isValid=true" in call_url
            assert "billType=Renewal" in call_url

    def test_get_bills_no_filter(self):
        """Test getting all bills without filters."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[]))
            api.get_bills()
            assert "?" not in mock.call_args[0][0]

    def test_get_bills_invalid_instance_id(self):
        """Test get_bills with invalid instance_id."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.get_bills(instance_id=-1)


class TestOrionBillingAdjustments:
    """Test OrionAPI billing adjustment methods."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            return OrionAPI(usr="test", pwd="pass")

    def test_get_adjustment_types(self):
        """Test getting adjustment types."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(
                json=Mock(return_value=[{"id": 1, "name": "Credit", "isDebit": False}])
            )
            result = api.get_adjustment_types()
            assert len(result) == 1
            assert result[0]["name"] == "Credit"

    def test_get_adjustment_types_with_filters(self):
        """Test getting adjustment types with filters."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[]))
            api.get_adjustment_types(is_payable=True, is_debit=False)
            call_url = mock.call_args[0][0]
            assert "isPayable=true" in call_url
            assert "isDebit=false" in call_url

    def test_get_recurring_adjustments(self):
        """Test getting recurring adjustments."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(
                json=Mock(
                    return_value=[{"id": 1, "additionalAnnualAmount": 1000.0, "type": "Dollar"}]
                )
            )
            result = api.get_recurring_adjustments()
            assert len(result) == 1
            assert result[0]["additionalAnnualAmount"] == 1000.0

    def test_get_recurring_adjustments_by_account(self):
        """Test getting recurring adjustments filtered by account."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[]))
            api.get_recurring_adjustments(account_id=123)
            assert "accountId=123" in mock.call_args[0][0]

    def test_get_recurring_adjustments_invalid_account(self):
        """Test get_recurring_adjustments with invalid account ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="account_id must be a positive integer"):
            api.get_recurring_adjustments(account_id=0)

    def test_get_household_recurring_adjustments(self):
        """Test getting household recurring adjustments."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(
                json=Mock(
                    return_value=[{"id": 1, "adjustmentId": 47, "additionalAnnualAmount": 500.0}]
                )
            )
            result = api.get_household_recurring_adjustments(household_id=456)
            assert len(result) == 1
            assert "householdId=456" in mock.call_args[0][0]

    def test_get_household_recurring_adjustments_invalid_id(self):
        """Test get_household_recurring_adjustments with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="household_id must be a positive integer"):
            api.get_household_recurring_adjustments(household_id=-1)

    def test_get_bill_item_adjustments(self):
        """Test getting bill item adjustments."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(
                json=Mock(return_value=[{"id": 1, "changeAmount": -50.0, "status": "Add"}])
            )
            result = api.get_bill_item_adjustments(bill_account_item_id=99)
            assert len(result) == 1
            assert result[0]["changeAmount"] == -50.0
            assert "/BillAccountAdj/99" in mock.call_args[0][0]

    def test_get_bill_item_adjustments_invalid_id(self):
        """Test get_bill_item_adjustments with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="bill_account_item_id must be a positive integer"):
            api.get_bill_item_adjustments(bill_account_item_id=0)

    def test_update_bill_item_adjustments(self):
        """Test updating bill item adjustments."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(
                json=Mock(return_value=[{"id": 10, "changeAmount": -100.0, "status": "Add"}])
            )
            adjustments = [{"adjustmentTypeId": 1, "changeAmount": -100.0, "status": "Add"}]
            result = api.update_bill_item_adjustments(
                bill_account_item_id=99, adjustments=adjustments
            )
            assert len(result) == 1
            call_url = mock.call_args[0][0]
            assert "/BillAccountAdj/edit/99" in call_url
            payload = mock.call_args[1]["json"]
            assert payload == adjustments

    def test_update_bill_item_adjustments_with_payable(self):
        """Test updating adjustments with createPayableAdj flag."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[]))
            api.update_bill_item_adjustments(
                bill_account_item_id=99,
                adjustments=[{"adjustmentTypeId": 1, "changeAmount": 50.0, "status": "Add"}],
                create_payable_adj=True,
            )
            assert "createPayableAdj=true" in mock.call_args[0][0]

    def test_update_bill_item_adjustments_invalid_id(self):
        """Test update_bill_item_adjustments with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="bill_account_item_id must be a positive integer"):
            api.update_bill_item_adjustments(bill_account_item_id=0, adjustments=[{}])

    def test_update_bill_item_adjustments_empty_list(self):
        """Test update_bill_item_adjustments with empty adjustments list."""
        api = self._make_api()
        with pytest.raises(ValueError, match="adjustments must be a non-empty list"):
            api.update_bill_item_adjustments(bill_account_item_id=1, adjustments=[])

    def test_update_bill_item_adjustments_not_list(self):
        """Test update_bill_item_adjustments with non-list adjustments."""
        api = self._make_api()
        with pytest.raises(ValueError, match="adjustments must be a non-empty list"):
            api.update_bill_item_adjustments(bill_account_item_id=1, adjustments="bad")


class TestOrionBillingOperations:
    """Test OrionAPI billing workflow gap methods."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            return OrionAPI(usr="test", pwd="pass")

    # --- Cash Funding ---

    def test_get_cash_funding(self):
        """Test getting cash funding data."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(
                json=Mock(
                    return_value=[
                        {"registrationName": "Acme", "balanceDue": 500.0, "accountNumber": "123"}
                    ]
                )
            )
            result = api.get_cash_funding(start_date="2026-01-01", end_date="2026-03-31")
            assert len(result) == 1
            assert result[0]["balanceDue"] == 500.0
            call_url = mock.call_args[0][0]
            assert "startDate=2026-01-01" in call_url
            assert "endDate=2026-03-31" in call_url
            assert "forecast=0" in call_url
            assert "take=10000" in call_url

    def test_get_cash_funding_forecast(self):
        """Test getting forecast cash funding data."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[]))
            api.get_cash_funding(start_date="2026-01-01", end_date="2026-03-31", is_forecast=True)
            call_url = mock.call_args[0][0]
            assert "forecast=1" in call_url

    def test_get_cash_funding_with_skip(self):
        """Test getting cash funding data with skip."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[]))
            api.get_cash_funding(start_date="2026-01-01", end_date="2026-03-31", skip=100)
            call_url = mock.call_args[0][0]
            assert "skip=100" in call_url

    def test_get_cash_funding_invalid_dates(self):
        """Test get_cash_funding with invalid dates."""
        api = self._make_api()
        with pytest.raises(ValueError, match="start_date must be a non-empty string"):
            api.get_cash_funding(start_date="", end_date="2026-03-31")
        with pytest.raises(ValueError, match="end_date must be a non-empty string"):
            api.get_cash_funding(start_date="2026-01-01", end_date="")

    def test_get_cash_funding_invalid_take(self):
        """Test get_cash_funding with invalid take."""
        api = self._make_api()
        with pytest.raises(ValueError, match="take must be a positive integer"):
            api.get_cash_funding(start_date="2026-01-01", end_date="2026-03-31", take=0)

    def test_generate_cash_funding(self):
        """Test generating cash funding data."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"success": True}))
            result = api.generate_cash_funding(instance_ids=[1, 2])
            assert result["success"] is True
            call_url = mock.call_args[0][0]
            assert "/Billing/Instances/GenerateCashFunding" in call_url
            assert "billInstanceIds=1" in call_url
            assert "billInstanceIds=2" in call_url

    def test_generate_cash_funding_with_dates(self):
        """Test generating cash funding with date range."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={}))
            api.generate_cash_funding(
                instance_ids=[1],
                start_date="2026-01-01",
                end_date="2026-03-31",
                is_forecast=True,
            )
            call_url = mock.call_args[0][0]
            assert "startDate=2026-01-01" in call_url
            assert "endDate=2026-03-31" in call_url
            assert "isForecast=true" in call_url

    def test_generate_cash_funding_invalid_ids(self):
        """Test generate_cash_funding with invalid instance_ids."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_ids must be a non-empty list"):
            api.generate_cash_funding(instance_ids=[])
        with pytest.raises(ValueError, match="instance_ids must be a non-empty list"):
            api.generate_cash_funding(instance_ids="bad")

    # --- Bill Management ---

    def test_delete_bills(self):
        """Test deleting bills."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[10, 20]))
            result = api.delete_bills(bill_ids=[10, 20])
            assert result == [10, 20]
            call_url = mock.call_args[0][0]
            assert "/Billing/Bills/Action/Delete" in call_url
            assert "deleteRelatedHouseholds" not in call_url
            payload = mock.call_args[1]["json"]
            assert payload == {"ids": [10, 20]}

    def test_delete_bills_with_related_households(self):
        """Test deleting bills with related households."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value=[10]))
            api.delete_bills(bill_ids=[10], delete_related_households=True)
            call_url = mock.call_args[0][0]
            assert "deleteRelatedHouseholds=true" in call_url

    def test_delete_bills_invalid_ids(self):
        """Test delete_bills with invalid bill_ids."""
        api = self._make_api()
        with pytest.raises(ValueError, match="bill_ids must be a non-empty list"):
            api.delete_bills(bill_ids=[])
        with pytest.raises(ValueError, match="bill_ids must be a non-empty list"):
            api.delete_bills(bill_ids="bad")

    # --- Receivables / Post Payment ---

    def test_get_receivables(self):
        """Test getting receivables for a billing instance."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"totalDue": 1500.0, "items": []}))
            result = api.get_receivables(instance_id=42)
            assert result["totalDue"] == 1500.0
            assert "/Billing/PostPayments/BillInstance/42" in mock.call_args[0][0]

    def test_get_receivables_invalid_id(self):
        """Test get_receivables with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.get_receivables(instance_id=0)
        with pytest.raises(ValueError, match="instance_id must be a positive integer"):
            api.get_receivables(instance_id=-1)

    def test_post_payments(self):
        """Test posting payments."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"posted": 2}))
            payments = [
                {"accountId": 1, "billId": 10, "amountToPost": 100.0},
                {"accountId": 2, "billId": 20, "amountToPost": 200.0},
            ]
            result = api.post_payments(batch_number="BATCH001", payments=payments)
            assert result["posted"] == 2
            call_url = mock.call_args[0][0]
            assert "batchNumber=BATCH001" in call_url
            payload = mock.call_args[1]["json"]
            assert len(payload) == 2

    def test_post_payments_invalid_batch(self):
        """Test post_payments with invalid batch number."""
        api = self._make_api()
        with pytest.raises(ValueError, match="batch_number must be a non-empty string"):
            api.post_payments(batch_number="", payments=[{"id": 1}])

    def test_post_payments_invalid_payments(self):
        """Test post_payments with invalid payments list."""
        api = self._make_api()
        with pytest.raises(ValueError, match="payments must be a non-empty list"):
            api.post_payments(batch_number="B1", payments=[])
        with pytest.raises(ValueError, match="payments must be a non-empty list"):
            api.post_payments(batch_number="B1", payments="bad")

    def test_write_off_bills(self):
        """Test writing off bills."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={"written_off": 1}))
            payments = [{"accountId": 1, "billId": 10, "amountToPost": 50.0}]
            result = api.write_off_bills(payments=payments)
            assert result["written_off"] == 1
            call_url = mock.call_args[0][0]
            assert "/Billing/PostPayments/WriteOffBills" in call_url
            assert "paymentFrom=Household" in call_url

    def test_write_off_bills_account_with_batch(self):
        """Test writing off bills from account with batch number."""
        api = self._make_api()
        with patch.object(api, "api_request") as mock:
            mock.return_value = Mock(json=Mock(return_value={}))
            api.write_off_bills(
                payments=[{"id": 1}],
                payment_from="Account",
                batch_number="WO-001",
            )
            call_url = mock.call_args[0][0]
            assert "paymentFrom=Account" in call_url
            assert "batchNumber=WO-001" in call_url

    def test_write_off_bills_invalid_payment_from(self):
        """Test write_off_bills with invalid payment_from."""
        api = self._make_api()
        with pytest.raises(ValueError, match="payment_from must be one of"):
            api.write_off_bills(payments=[{"id": 1}], payment_from="Invalid")

    def test_write_off_bills_invalid_payments(self):
        """Test write_off_bills with invalid payments list."""
        api = self._make_api()
        with pytest.raises(ValueError, match="payments must be a non-empty list"):
            api.write_off_bills(payments=[])


class TestOrionHierarchyManagement:
    """Test OrionAPI hierarchy management methods."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"):
            return OrionAPI(usr="test", pwd="pass")

    def _make_api_with_mock(self):
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")
        return api

    def test_create_client(self):
        """Test creating a client."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 1, "name": "Test Household"}
            mock_req.return_value = mock_resp

            result = api.create_client({"name": "Test Household"})

            mock_req.assert_called_once()
            call_args = mock_req.call_args
            assert "Portfolio/Clients/Verbose" in call_args[0][0]
            assert call_args[1]["json"] == {"name": "Test Household"}
            assert result["name"] == "Test Household"

    def test_create_client_invalid_data(self):
        """Test create_client with invalid data."""
        api = self._make_api()
        with pytest.raises(ValueError, match="data must be a non-empty dict"):
            api.create_client({})
        with pytest.raises(ValueError, match="data must be a non-empty dict"):
            api.create_client("not a dict")

    def test_cancel_client_full(self):
        """Test full client cancellation."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"success": True}
            mock_req.return_value = mock_resp

            api.cancel_client(client_id=1, cancel_type="Full")

            mock_req.assert_called_once()
            call_args = mock_req.call_args
            assert "Portfolio/Clients/Action/Cancel" in call_args[0][0]
            body = call_args[1]["json"]
            assert body["clientId"] == 1
            assert body["cancelType"] == "Full"

    def test_cancel_client_partial(self):
        """Test partial client cancellation with account IDs."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"success": True}
            mock_req.return_value = mock_resp

            api.cancel_client(client_id=1, cancel_type="Partial", account_ids=[10, 20])

            body = mock_req.call_args[1]["json"]
            assert body["cancelType"] == "Partial"
            assert body["accountIds"] == [10, 20]

    def test_cancel_client_partial_no_accounts(self):
        """Test partial cancellation without account_ids raises ValueError."""
        api = self._make_api()
        with pytest.raises(ValueError, match="account_ids must be a non-empty list"):
            api.cancel_client(client_id=1, cancel_type="Partial")

    def test_delete_clients(self):
        """Test deleting clients."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [1, 2]
            mock_req.return_value = mock_resp

            result = api.delete_clients([1, 2])

            call_args = mock_req.call_args
            assert "Portfolio/Clients/Action/Delete" in call_args[0][0]
            assert call_args[1]["json"] == [1, 2]
            assert result == [1, 2]

    def test_delete_clients_invalid(self):
        """Test delete_clients with empty list."""
        api = self._make_api()
        with pytest.raises(ValueError, match="client_ids must be a non-empty list"):
            api.delete_clients([])

    def test_get_portfolio_tree(self):
        """Test getting portfolio tree."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"clientId": 1, "registrations": []}
            mock_req.return_value = mock_resp

            result = api.get_portfolio_tree(client_id=1, filter_type="AccountsOnly")

            call_url = mock_req.call_args[0][0]
            assert "Portfolio/Clients/1/PortfolioTree" in call_url
            assert "filterType=AccountsOnly" in call_url
            assert result["clientId"] == 1

    def test_get_portfolio_tree_invalid_id(self):
        """Test get_portfolio_tree with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="client_id must be a positive integer"):
            api.get_portfolio_tree(client_id=0)

    def test_create_registration(self):
        """Test creating a registration."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 10, "name": "Test Reg"}
            mock_req.return_value = mock_resp

            data = {"name": "Test Reg", "portfolio": {"clientId": 1}}
            result = api.create_registration(data)

            call_args = mock_req.call_args
            assert "Portfolio/Registrations/Verbose" in call_args[0][0]
            assert call_args[1]["json"] == data
            assert result["name"] == "Test Reg"

    def test_move_registration(self):
        """Test moving registrations to a different client."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"success": True}
            mock_req.return_value = mock_resp

            api.move_registration(registration_ids=[10, 20], target_client_id=5)

            call_args = mock_req.call_args
            assert "Portfolio/Registrations/Action/MoveToClient/5" in call_args[0][0]
            assert call_args[1]["json"] == [10, 20]

    def test_move_registration_invalid(self):
        """Test move_registration with invalid parameters."""
        api = self._make_api()
        with pytest.raises(ValueError, match="registration_ids must be a non-empty list"):
            api.move_registration(registration_ids=[], target_client_id=5)
        with pytest.raises(ValueError, match="target_client_id must be a positive integer"):
            api.move_registration(registration_ids=[1], target_client_id=0)

    def test_split_registration(self):
        """Test splitting a registration."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"success": True}
            mock_req.return_value = mock_resp

            api.split_registration(registration_id=10)

            call_url = mock_req.call_args[0][0]
            assert "Portfolio/Registrations/10/Action/Split" in call_url

    def test_split_registration_invalid_id(self):
        """Test split_registration with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="registration_id must be a positive integer"):
            api.split_registration(registration_id=-1)

    def test_delete_registrations(self):
        """Test deleting registrations."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [10, 20]
            mock_req.return_value = mock_resp

            result = api.delete_registrations([10, 20])

            call_args = mock_req.call_args
            assert "Portfolio/Registrations/Action/Delete" in call_args[0][0]
            assert call_args[1]["json"] == [10, 20]
            assert result == [10, 20]

    def test_create_orion_account(self):
        """Test creating an account."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 100, "name": "Test Account"}
            mock_req.return_value = mock_resp

            data = {"name": "Test Account", "number": "12345"}
            result = api.create_orion_account(data)

            call_args = mock_req.call_args
            assert "Portfolio/Accounts/Verbose" in call_args[0][0]
            assert "generateAccountNumber" not in call_args[0][0]
            assert call_args[1]["json"] == data
            assert result["name"] == "Test Account"

    def test_create_orion_account_generate_number(self):
        """Test creating an account with auto-generated number."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 100}
            mock_req.return_value = mock_resp

            api.create_orion_account({"name": "Test"}, generate_account_number=True)

            call_url = mock_req.call_args[0][0]
            assert "generateAccountNumber=true" in call_url

    def test_move_account(self):
        """Test moving an account to a different registration."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 100}
            mock_req.return_value = mock_resp

            api.move_account(account_id=100, target_registration_id=50)

            call_url = mock_req.call_args[0][0]
            assert "Portfolio/Accounts/100/Action/MoveToRegistration/50" in call_url

    def test_move_account_invalid(self):
        """Test move_account with invalid IDs."""
        api = self._make_api()
        with pytest.raises(ValueError, match="account_id must be a positive integer"):
            api.move_account(account_id=0, target_registration_id=5)
        with pytest.raises(ValueError, match="target_registration_id must be a positive integer"):
            api.move_account(account_id=1, target_registration_id=-1)

    def test_merge_accounts(self):
        """Test merging accounts."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [1, 2]
            mock_req.return_value = mock_resp

            merges = [{"oldAccountId": 1, "newAccountId": 2}]
            result = api.merge_accounts(merges)

            call_args = mock_req.call_args
            assert "Portfolio/Accounts/Action/Merge" in call_args[0][0]
            assert call_args[1]["json"] == merges
            assert result == [1, 2]

    def test_merge_accounts_invalid(self):
        """Test merge_accounts with empty list."""
        api = self._make_api()
        with pytest.raises(ValueError, match="merges must be a non-empty list"):
            api.merge_accounts([])

    def test_convert_account(self):
        """Test converting an account."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 200}
            mock_req.return_value = mock_resp

            result = api.convert_account(
                from_account_id=100, convert_date="2026-01-01", copy_assets=True
            )

            call_args = mock_req.call_args
            assert "Portfolio/Accounts/Action/ConvertAccount" in call_args[0][0]
            body = call_args[1]["json"]
            assert body["fromAccountId"] == 100
            assert body["convertDate"] == "2026-01-01"
            assert body["copyAssets"] is True
            assert result["id"] == 200

    def test_convert_account_invalid_id(self):
        """Test convert_account with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="from_account_id must be a positive integer"):
            api.convert_account(from_account_id=0, convert_date="2026-01-01")

    def test_delete_accounts(self):
        """Test deleting accounts."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [100, 200]
            mock_req.return_value = mock_resp

            result = api.delete_accounts([100, 200])

            call_args = mock_req.call_args
            assert "Portfolio/Accounts/Action/Delete" in call_args[0][0]
            assert call_args[1]["json"] == [100, 200]
            assert result == [100, 200]

    def test_undo_account_conversion(self):
        """Test undoing an account conversion."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"success": True}
            mock_req.return_value = mock_resp

            import requests

            api.undo_account_conversion(account_id=100)

            call_args = mock_req.call_args
            assert "Portfolio/Accounts/100/Action/UndoConversion" in call_args[0][0]
            assert call_args[0][1] == requests.delete


class TestOrionTransactions:
    """Test OrionAPI transaction methods."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"):
            return OrionAPI(usr="test", pwd="pass")

    def _make_api_with_mock(self):
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")
        return api

    def test_get_transactions_no_filter(self):
        """Test getting transactions without filters."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [{"id": 1, "transAmount": 100}]
            mock_req.return_value = mock_resp

            result = api.get_transactions()

            call_url = mock_req.call_args[0][0]
            assert "Portfolio/Transactions" in call_url
            assert "?" not in call_url
            assert len(result) == 1

    def test_get_transactions_by_account(self):
        """Test getting transactions filtered by account."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = []
            mock_req.return_value = mock_resp

            api.get_transactions(account_id=123)

            call_url = mock_req.call_args[0][0]
            assert "accountId=123" in call_url

    def test_get_transactions_by_date_range(self):
        """Test getting transactions filtered by date range."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = []
            mock_req.return_value = mock_resp

            api.get_transactions(start_date="2026-01-01", end_date="2026-03-31")

            call_url = mock_req.call_args[0][0]
            assert "startDate=2026-01-01" in call_url
            assert "endDate=2026-03-31" in call_url

    def test_get_transactions_by_status(self):
        """Test getting transactions filtered by status."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = []
            mock_req.return_value = mock_resp

            api.get_transactions(status="Complete")

            call_url = mock_req.call_args[0][0]
            assert "status=Complete" in call_url

    def test_get_transactions_invalid_status(self):
        """Test get_transactions with invalid status."""
        api = self._make_api()
        with pytest.raises(ValueError, match="status must be one of"):
            api.get_transactions(status="InvalidStatus")

    def test_get_transactions_invalid_account_id(self):
        """Test get_transactions with invalid account_id."""
        api = self._make_api()
        with pytest.raises(ValueError, match="account_id must be a positive integer"):
            api.get_transactions(account_id=0)


class TestOrionReportBatches:
    """Test OrionAPI report batch methods."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"):
            return OrionAPI(usr="test", pwd="pass")

    def _make_api_with_mock(self):
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")
        return api

    def test_get_report_batches(self):
        """Test listing report batches."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [{"id": 1, "name": "Q1 2026"}]
            mock_req.return_value = mock_resp

            result = api.get_report_batches()

            call_url = mock_req.call_args[0][0]
            assert "Reporting/Batch" in call_url
            assert "?" not in call_url
            assert len(result) == 1

    def test_get_report_batches_with_filter(self):
        """Test listing report batches with QPE filter."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = []
            mock_req.return_value = mock_resp

            api.get_report_batches(qpe_item_id=42)

            call_url = mock_req.call_args[0][0]
            assert "qpeItemId=42" in call_url

    def test_get_report_batch(self):
        """Test getting a single report batch."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = {"id": 5, "name": "Batch 5"}
            mock_req.return_value = mock_resp

            result = api.get_report_batch(batch_id=5)

            call_url = mock_req.call_args[0][0]
            assert "Reporting/Batch/5" in call_url
            assert result["id"] == 5

    def test_get_report_batch_invalid_id(self):
        """Test get_report_batch with invalid ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="batch_id must be a positive integer"):
            api.get_report_batch(batch_id=0)

    def test_get_report_batch_entities(self):
        """Test getting batch entities."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [{"id": 1, "entityName": "Client A"}]
            mock_req.return_value = mock_resp

            result = api.get_report_batch_entities(batch_id=5)

            call_url = mock_req.call_args[0][0]
            assert "Reporting/Batch/5/Entities" in call_url
            assert len(result) == 1

    def test_get_report_batch_entities_by_status(self):
        """Test getting batch entities filtered by generation status."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = []
            mock_req.return_value = mock_resp

            api.get_report_batch_entities(batch_id=5, generation_status="Generated")

            call_url = mock_req.call_args[0][0]
            assert "generationStatus=Generated" in call_url

    def test_generate_statements(self):
        """Test generating statements with entity IDs."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [1, 2, 3]
            mock_req.return_value = mock_resp

            import requests

            result = api.generate_statements(batch_id=5, entity_ids=[1, 2, 3])

            call_args = mock_req.call_args
            assert "Reporting/Batch/5/Entities/Action/Generate" in call_args[0][0]
            assert call_args[0][1] == requests.post
            assert call_args[1]["json"] == [1, 2, 3]
            assert result == [1, 2, 3]

    def test_generate_statements_all(self):
        """Test generating all statements (no entity IDs)."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = []
            mock_req.return_value = mock_resp

            api.generate_statements(batch_id=5)

            call_args = mock_req.call_args
            assert "Reporting/Batch/5/Entities/Action/Generate" in call_args[0][0]
            assert "json" not in call_args[1]

    def test_generate_statements_invalid_id(self):
        """Test generate_statements with invalid batch ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="batch_id must be a positive integer"):
            api.generate_statements(batch_id=-1)

    def test_send_electronic_statements(self):
        """Test sending electronic statements."""
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_resp = Mock()
            mock_resp.json.return_value = [1, 2]
            mock_req.return_value = mock_resp

            import requests

            result = api.send_electronic_statements(batch_id=5, entity_ids=[1, 2])

            call_args = mock_req.call_args
            assert "Reporting/Batch/5/Entities/Action/SendElectronicStatement" in call_args[0][0]
            assert call_args[0][1] == requests.post
            assert call_args[1]["json"] == [1, 2]
            assert result == [1, 2]

    def test_send_electronic_statements_invalid_id(self):
        """Test send_electronic_statements with invalid batch ID."""
        api = self._make_api()
        with pytest.raises(ValueError, match="batch_id must be a positive integer"):
            api.send_electronic_statements(batch_id=0)


class TestDownloadReportPdf:
    """Test OrionAPI.download_report_pdf."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"):
            return OrionAPI(usr="test", pwd="pass")

    def _make_api_with_mock(self):
        with patch.object(OrionAPI, "login"), patch.object(
            OrionAPI, "_get_auth_header", return_value={}
        ):
            api = OrionAPI(usr="test", pwd="pass")
        return api

    def _pdf_response(self, content=b"%PDF-1.4\n%fake body bytes", content_type="application/pdf"):
        resp = Mock()
        resp.content = content
        resp.headers = {"Content-Type": content_type}
        return resp

    def test_download_returns_bytes(self):
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_req.return_value = self._pdf_response()

            result = api.download_report_pdf(batch_id=5, entity_key=42)

            call_args = mock_req.call_args
            assert "Reporting/Batch/5/Entities/42/Action/Download" in call_args[0][0]
            assert call_args[1]["headers"] == {"Accept": "application/pdf"}
            assert result.startswith(b"%PDF-")

    def test_download_accepts_octet_stream(self):
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_req.return_value = self._pdf_response(content_type="application/octet-stream")

            result = api.download_report_pdf(batch_id=5, entity_key=42)
            assert result.startswith(b"%PDF-")

    def test_download_rejects_html(self):
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_req.return_value = self._pdf_response(
                content=b"<html><body>error page</body></html>",
                content_type="text/html",
            )

            with pytest.raises(OrionAPIError, match="Expected PDF response"):
                api.download_report_pdf(batch_id=5, entity_key=42)

    def test_download_rejects_wrong_magic_bytes(self):
        api = self._make_api_with_mock()
        with patch.object(api, "api_request") as mock_req:
            mock_req.return_value = self._pdf_response(
                content=b"NOT A PDF AT ALL",
                content_type="application/pdf",
            )

            with pytest.raises(OrionAPIError, match="Expected PDF response"):
                api.download_report_pdf(batch_id=5, entity_key=42)

    def test_download_invalid_args(self):
        api = self._make_api()
        with pytest.raises(ValueError, match="batch_id must be a positive integer"):
            api.download_report_pdf(batch_id=0, entity_key=1)
        with pytest.raises(ValueError, match="batch_id must be a positive integer"):
            api.download_report_pdf(batch_id="5", entity_key=1)
        with pytest.raises(ValueError, match="entity_key must be a positive integer"):
            api.download_report_pdf(batch_id=5, entity_key=0)
        with pytest.raises(ValueError, match="entity_key must be a positive integer"):
            api.download_report_pdf(batch_id=5, entity_key=-1)


class TestPollUntilGenerated:
    """Test OrionAPI.poll_until_generated."""

    def _make_api(self):
        with patch.object(OrionAPI, "login"):
            return OrionAPI(usr="test", pwd="pass")

    def test_returns_when_all_terminal(self):
        api = self._make_api()
        entities = [
            {"id": 1, "generationStatus": "Generated"},
            {"id": 2, "generationStatus": "ErroredReport"},
        ]
        with patch.object(api, "get_report_batch_entities", return_value=entities), patch(
            "orionapi.time.sleep"
        ) as mock_sleep:
            result = api.poll_until_generated(batch_id=5)

            assert result == entities
            mock_sleep.assert_not_called()

    def test_polls_until_done(self):
        api = self._make_api()
        progress = [
            [{"id": 1, "generationStatus": "PendingGeneration"}],
            [{"id": 1, "generationStatus": "PendingGeneration"}],
            [{"id": 1, "generationStatus": "Generated"}],
        ]
        with patch.object(
            api, "get_report_batch_entities", side_effect=progress
        ) as mock_get, patch("orionapi.time.sleep"):
            result = api.poll_until_generated(batch_id=5, poll_interval=1)

            assert result == progress[-1]
            assert mock_get.call_count == 3

    def test_progress_callback_invoked(self):
        api = self._make_api()
        entities = [
            {"id": 1, "generationStatus": "Generated"},
            {"id": 2, "generationStatus": "PendingGeneration"},
            {"id": 3, "generationStatus": "ErroredReport"},
        ]
        calls = []
        second = [dict(e, generationStatus="Generated") for e in entities]
        with patch.object(api, "get_report_batch_entities", side_effect=[entities, second]), patch(
            "orionapi.time.sleep"
        ):
            api.poll_until_generated(
                batch_id=5,
                progress_callback=lambda done, total: calls.append((done, total)),
            )

        assert calls == [(2, 3), (3, 3)]

    def test_progress_callback_skipped_when_unchanged(self):
        api = self._make_api()
        pending = [{"id": 1, "generationStatus": "PendingGeneration"}]
        done = [{"id": 1, "generationStatus": "Generated"}]
        calls = []
        with patch.object(
            api, "get_report_batch_entities", side_effect=[pending, pending, pending, done]
        ), patch("orionapi.time.sleep"):
            api.poll_until_generated(
                batch_id=5,
                progress_callback=lambda done, total: calls.append((done, total)),
            )
        assert calls == [(0, 1), (1, 1)]

    def test_timeout_raises(self):
        api = self._make_api()
        pending = [{"id": 1, "generationStatus": "PendingGeneration"}]
        with patch.object(api, "get_report_batch_entities", return_value=pending), patch(
            "orionapi.time.monotonic", side_effect=[0, 1000]
        ), patch("orionapi.time.sleep"):
            with pytest.raises(TimeoutError, match="did not finish generating"):
                api.poll_until_generated(batch_id=5, timeout=10)

    def test_invalid_args(self):
        api = self._make_api()
        with pytest.raises(ValueError, match="batch_id must be a positive integer"):
            api.poll_until_generated(batch_id=0)
        with pytest.raises(ValueError, match="timeout must be a positive number"):
            api.poll_until_generated(batch_id=5, timeout=0)
        with pytest.raises(ValueError, match="poll_interval must be a positive number"):
            api.poll_until_generated(batch_id=5, poll_interval=-1)
