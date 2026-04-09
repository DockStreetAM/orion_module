"""Unit tests for newly added API endpoints.

Tests for OrionAPI and EclipseAPI methods added in v1.4.0.
"""

from unittest.mock import Mock, patch

import pytest

from orionapi import EclipseAPI, OrionAPI


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
