"""Integration tests that require real API credentials.

These tests are skipped if ECLIPSE_USER/ECLIPSE_PWD are not set.
To run: copy .env.example to .env, fill in credentials, then run pytest.
"""

import pytest


class TestEclipseAPI:
    def test_check_username(self, eclipse_client):
        """Test that we can authenticate and get username."""
        username = eclipse_client.check_username()
        assert username is not None
        assert len(username) > 0

    def test_get_all_accounts(self, eclipse_client):
        """Test that we can fetch accounts."""
        accounts = eclipse_client.get_all_accounts()
        assert isinstance(accounts, list)

    def test_get_portfolio(self, eclipse_client):
        """Test that we can fetch a portfolio by ID."""
        # Get list of accounts first to find a valid portfolio
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        # Try to get a portfolio - accounts have portfolioId
        portfolio_id = accounts[0].get("portfolioId")
        if not portfolio_id:
            pytest.skip("No portfolio ID found in accounts")

        portfolio = eclipse_client.get_portfolio(portfolio_id)
        assert "general" in portfolio
        assert "portfolioName" in portfolio["general"]

    def test_get_all_models(self, eclipse_client):
        """Test that we can fetch models."""
        models = eclipse_client.get_all_models()
        assert isinstance(models, list)

    def test_get_orders(self, eclipse_client):
        """Test that we can fetch orders."""
        orders = eclipse_client.get_orders()
        assert isinstance(orders, list)

    def test_get_all_portfolios(self, eclipse_client):
        """Test that we can fetch all portfolios with values."""
        portfolios = eclipse_client.get_all_portfolios(include_value=True)
        assert isinstance(portfolios, list)
        if portfolios:
            assert "id" in portfolios[0]

    def test_get_all_portfolios_with_search(self, eclipse_client):
        """Test fetching portfolios with search filter."""
        # Get all portfolios first to find a name to search for
        all_portfolios = eclipse_client.get_all_portfolios()
        if not all_portfolios:
            pytest.skip("No portfolios available")

        # Use part of the first portfolio's name
        search_term = all_portfolios[0].get("portfolioName", "")[:3]
        if not search_term:
            pytest.skip("No portfolio name to search")

        filtered = eclipse_client.get_all_portfolios(search=search_term)
        assert isinstance(filtered, list)
        # Search should return subset or equal
        assert len(filtered) <= len(all_portfolios)

    def test_get_portfolio_accounts(self, eclipse_client):
        """Test that we can fetch accounts for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        accounts = eclipse_client.get_portfolio_accounts(portfolio_id)
        assert isinstance(accounts, list)

    def test_get_portfolio_holdings(self, eclipse_client):
        """Test that we can fetch holdings for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        holdings = eclipse_client.get_portfolio_holdings(portfolio_id)
        assert isinstance(holdings, list)

    def test_get_portfolio_holdings_with_search(self, eclipse_client):
        """Test fetching portfolio holdings with search filter."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        all_holdings = eclipse_client.get_portfolio_holdings(portfolio_id)
        if not all_holdings:
            pytest.skip("No holdings available")

        # Use part of the first holding's ticker/symbol if available
        search_term = all_holdings[0].get("ticker", all_holdings[0].get("symbol", ""))[:2]
        if not search_term:
            pytest.skip("No searchable holding field found")

        filtered = eclipse_client.get_portfolio_holdings(portfolio_id, search=search_term)
        assert isinstance(filtered, list)
        # Search should return subset or equal
        assert len(filtered) <= len(all_holdings)

    def test_get_account_holdings(self, eclipse_client):
        """Test that we can fetch holdings for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        holdings = eclipse_client.get_account_holdings(account_id)
        assert isinstance(holdings, list)

    def test_get_account_holdings_with_search(self, eclipse_client):
        """Test fetching account holdings with search filter."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        all_holdings = eclipse_client.get_account_holdings(account_id)
        if not all_holdings:
            pytest.skip("No holdings available")

        # Use part of the first holding's ticker/symbol if available
        search_term = all_holdings[0].get("ticker", all_holdings[0].get("symbol", ""))[:2]
        if not search_term:
            pytest.skip("No searchable holding field found")

        filtered = eclipse_client.get_account_holdings(account_id, search=search_term)
        assert isinstance(filtered, list)
        # Search should return subset or equal
        assert len(filtered) <= len(all_holdings)

    # High priority tests

    def test_get_account_details(self, eclipse_client):
        """Test that we can fetch details for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        details = eclipse_client.get_account_details(account_id)
        assert isinstance(details, dict)
        assert "id" in details or "accountNumber" in details

    def test_get_model(self, eclipse_client):
        """Test that we can fetch a model by ID."""
        models = eclipse_client.get_all_models()
        if not models:
            pytest.skip("No models available")

        model_id = models[0]["id"]
        model = eclipse_client.get_model(model_id)
        assert isinstance(model, dict)
        assert "id" in model

    def test_get_model_tolerance(self, eclipse_client):
        """Test that we can fetch model tolerance for a portfolio/account."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        accounts = eclipse_client.get_portfolio_accounts(portfolio_id)
        if not accounts:
            pytest.skip("No accounts in portfolio")

        account_id = accounts[0]["id"]
        tolerance = eclipse_client.get_model_tolerance(portfolio_id, account_id)
        assert isinstance(tolerance, (dict, list))

    def test_search_accounts_number_and_name(self, eclipse_client):
        """Test that we can search accounts by number and name."""
        # Get an existing account to use for search
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        # Use last 4 digits of account number and part of name
        acct = accounts[0]
        acct_num = acct.get("accountNumber", "")
        acct_name = acct.get("name", "")

        if not acct_num or not acct_name:
            pytest.skip("Account missing number or name")

        # Search using trailing digits and name portion
        acct_id, found_num = eclipse_client.search_accounts_number_and_name(
            acct_num[-4:], acct_name[:5]
        )
        assert isinstance(acct_id, int)
        assert isinstance(found_num, str)

    # Medium priority tests

    def test_get_model_allocations(self, eclipse_client):
        """Test that we can fetch model allocations."""
        models = eclipse_client.get_all_models()
        if not models:
            pytest.skip("No models available")

        model_id = models[0]["id"]
        allocations = eclipse_client.get_model_allocations(model_id)
        assert isinstance(allocations, (dict, list))

    def test_get_set_asides(self, eclipse_client):
        """Test that we can fetch set asides for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        # Use accountNumber (not id) since get_set_asides resolves via search
        account_number = accounts[0].get("accountNumber")
        if not account_number:
            pytest.skip("First account has no accountNumber")
        set_asides = eclipse_client.get_set_asides(account_number)
        assert isinstance(set_asides, (dict, list))

    def test_get_all_security_sets(self, eclipse_client):
        """Test that we can fetch all security sets."""
        security_sets = eclipse_client.get_all_security_sets()
        assert isinstance(security_sets, list)

    # Additional read method tests

    def test_get_orders_pending(self, eclipse_client):
        """Test that we can fetch pending orders."""
        orders = eclipse_client.get_orders_pending()
        assert isinstance(orders, list)

    def test_get_all_account_details(self, eclipse_client):
        """Test that we can fetch details for all accounts."""
        details = eclipse_client.get_all_account_details()
        assert isinstance(details, list)

    def test_get_internal_account_id(self, eclipse_client):
        """Test that we can get internal account ID from account number."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        acct_num = accounts[0].get("accountNumber", "")
        if not acct_num:
            pytest.skip("Account missing number")

        internal_id = eclipse_client.get_internal_account_id(acct_num)
        assert isinstance(internal_id, int)

    def test_get_account_cash_available(self, eclipse_client):
        """Test that we can get available cash for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]
        cash = eclipse_client.get_account_cash_available(account_id)
        assert isinstance(cash, (int, float))

    def test_get_security_set(self, eclipse_client):
        """Test that we can fetch a security set by ID."""
        security_sets = eclipse_client.get_all_security_sets()
        if not security_sets:
            pytest.skip("No security sets available")

        set_id = security_sets[0]["id"]
        security_set = eclipse_client.get_security_set(set_id)
        assert isinstance(security_set, dict)

    def test_get_set_asides_firmwide(self, eclipse_client):
        """Test that we can fetch set asides firm-wide via the v2 batch endpoint."""
        set_asides = eclipse_client.get_set_asides()
        assert isinstance(set_asides, list)
        if set_asides:
            assert "set_aside_id" in set_asides[0]
            assert "account_number" in set_asides[0]

    def test_search_securities(self, eclipse_client):
        """Test that we can search for securities."""
        results = eclipse_client.search_securities("AAPL", top=5)
        assert isinstance(results, list)
        # Should find at least one result
        assert len(results) > 0
        # Check structure
        assert "id" in results[0]
        assert "symbol" in results[0] or "name" in results[0]

    def test_get_security_by_ticker(self, eclipse_client):
        """Test that we can get a security by ticker."""
        sec = eclipse_client.get_security_by_ticker("AAPL")
        assert isinstance(sec, dict)
        assert "id" in sec
        assert sec.get("symbol", "").upper() == "AAPL"

    def test_parse_security_set_file(self, eclipse_client, tmp_path):
        """Test parsing a security set definition file."""
        # Create a test file
        test_file = tmp_path / "test_set.txt"
        test_file.write_text("""# Security Set: Test Set
# Description: A test security set

# Ticker  Lower%  Target%  Upper%
AAPL      5       10       20
MSFT      3       8        15
""")

        parsed = eclipse_client.parse_security_set_file(str(test_file))
        assert parsed["name"] == "Test Set"
        assert parsed["description"] == "A test security set"
        assert len(parsed["securities"]) == 2
        assert parsed["securities"][0]["ticker"] == "AAPL"
        assert parsed["securities"][0]["lower_bound"] == 5.0
        assert parsed["securities"][0]["target"] == 10.0
        assert parsed["securities"][0]["upper_bound"] == 20.0

    def test_convert_to_eclipse_tolerances(self, eclipse_client):
        """Test converting absolute bounds to Eclipse tolerance format."""
        securities = [{"ticker": "AAPL", "lower_bound": 5, "target": 10, "upper_bound": 20}]
        result = eclipse_client.convert_to_eclipse_tolerances(securities)
        assert len(result) == 1
        assert "id" in result[0]
        assert result[0]["targetPercent"] == 10
        # lower_tolerance = target - lower_bound = 10 - 5 = 5
        assert result[0]["lowerModelTolerancePercent"] == 5
        # upper_tolerance = upper_bound - target = 20 - 10 = 10
        assert result[0]["upperModelTolerancePercent"] == 10

    def test_get_analytics_status(self, eclipse_client):
        """Test checking analytics status."""
        status = eclipse_client.get_analytics_status()
        assert isinstance(status, dict)
        assert "isAnalysisRunning" in status or "doRunAnalytics" in status

    def test_get_closed_trades(self, eclipse_client):
        """Test fetching closed/executed trades."""
        trades = eclipse_client.get_closed_trades()
        assert isinstance(trades, list)

    def test_get_trade_instances(self, eclipse_client):
        """Test fetching trade instances by date range."""
        # Use a recent date range (last 30 days)
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        instances = eclipse_client.get_trade_instances(start_date, end_date)
        assert isinstance(instances, list)

    def test_search_accounts(self, eclipse_client):
        """Test searching accounts by various criteria."""
        # Get an account to use as search term
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        # Search using part of the first account's name or number
        search_term = accounts[0].get("accountName", accounts[0].get("accountNumber", ""))[:3]
        if not search_term:
            pytest.skip("No searchable account field found")

        results = eclipse_client.search_accounts(search_term)
        assert isinstance(results, list)

    def test_get_security_preferences(self, eclipse_client):
        """Test fetching security preferences for a portfolio and security."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]
        holdings = eclipse_client.get_portfolio_holdings(portfolio_id)
        if not holdings:
            pytest.skip("No holdings available")

        security_id = holdings[0].get("securityId")
        if not security_id:
            pytest.skip("No security ID found")

        prefs = eclipse_client.get_security_preferences(portfolio_id, security_id)
        assert isinstance(prefs, dict)

    def test_get_trade_status(self, eclipse_client):
        """Test fetching trade status."""
        orders = eclipse_client.get_orders()
        if not orders:
            pytest.skip("No orders available")

        trade_id = orders[0]["id"]
        status = eclipse_client.get_trade_status(trade_id)
        assert isinstance(status, dict)

    def test_get_trade_instance(self, eclipse_client):
        """Test fetching trade instance details."""
        # Try to get a recent instance - we know instance 4891 exists from testing
        try:
            instance = eclipse_client.get_trade_instance(4891)
            assert isinstance(instance, dict)
            assert "id" in instance
            assert "executeStatus" in instance
        except Exception:
            pytest.skip("Instance 4891 not available or test environment changed")

    def test_get_trade_instance_logs(self, eclipse_client):
        """Test fetching trade instance logs."""
        # Try to get logs for instance 4891
        try:
            logs = eclipse_client.get_trade_instance_logs(4891)
            assert isinstance(logs, list)
            # Logs may be empty or contain entries
            if logs:
                assert "tradeInstanceId" in logs[0]
        except Exception:
            pytest.skip("Instance 4891 not available or test environment changed")

    def test_get_trade_log_detail(self, eclipse_client):
        """Test fetching detailed HTML trade log."""
        # Get logs for instance 4891
        try:
            logs = eclipse_client.get_trade_instance_logs(4891)
            if not logs:
                pytest.skip("No logs available for instance 4891")

            log_id = logs[0]["id"]

            # Get detailed HTML log
            html = eclipse_client.get_trade_log_detail(log_id)

            assert isinstance(html, str)
            assert len(html) > 0
            # Should be HTML content
            assert "<" in html or "html" in html.lower()
        except Exception as e:
            pytest.skip(f"Instance 4891 or log detail not available: {e}")

    def test_get_portfolio_trade_instances(self, eclipse_client):
        """Test fetching trade instances for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]

        # Get instances for the last 30 days
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        instances = eclipse_client.get_portfolio_trade_instances(portfolio_id, start_date, end_date)

        assert isinstance(instances, list)
        # May be empty if no instances in date range
        if instances:
            assert "id" in instances[0]
            assert "executeStatus" in instances[0]

    @pytest.mark.skip(reason="Skipping write method - only testing read-only methods")
    def test_set_portfolio_tradeable(self, eclipse_client):
        """Test blocking and unblocking trading for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]

        # Block trading
        eclipse_client.set_portfolio_tradeable(portfolio_id, tradeable=False, sync=False)
        portfolio = eclipse_client.get_portfolio(portfolio_id)
        assert portfolio["general"]["doNotTrade"] == 1

        # Unblock trading
        eclipse_client.set_portfolio_tradeable(portfolio_id, tradeable=True, sync=False)
        portfolio = eclipse_client.get_portfolio(portfolio_id)
        assert portfolio["general"]["doNotTrade"] == 0

    @pytest.mark.skip(reason="Skipping write method - only testing read-only methods")
    def test_set_account_tradeable(self, eclipse_client):
        """Test setting trade restrictions for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]["id"]

        # Test blocking advisor
        eclipse_client.set_account_tradeable(
            account_id, trade_restriction="block_advisor", sync=False
        )
        account = eclipse_client.get_account_details(account_id)
        assert account["generalSection"]["doNotTrade"] == 1
        assert account["generalSection"]["doNotTradeCustodian"] == 0

        # Test blocking custodian
        eclipse_client.set_account_tradeable(
            account_id, trade_restriction="block_custodian", sync=False
        )
        account = eclipse_client.get_account_details(account_id)
        assert account["generalSection"]["doNotTrade"] == 0
        assert account["generalSection"]["doNotTradeCustodian"] == 1

        # Test making tradeable again
        eclipse_client.set_account_tradeable(account_id, trade_restriction="tradeable", sync=False)
        account = eclipse_client.get_account_details(account_id)
        assert account["generalSection"]["doNotTrade"] == 0
        assert account["generalSection"]["doNotTradeCustodian"] == 0

    @pytest.mark.skip(reason="Skipping write method - only testing read-only methods")
    def test_spend_cash_trade(self, eclipse_client):
        """Test generating Spend Cash trade."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]["id"]

        # Generate trade in view-only mode
        result = eclipse_client.spend_cash_trade(
            portfolio_ids=[portfolio_id],
            reason="Integration test spend cash",
            is_view_only=True,
            sync=False,
        )

        assert isinstance(result, dict)
        assert "success" in result
        # View-only mode should still create an instance
        if result.get("success"):
            assert "instanceId" in result

    # Edge case tests

    def test_get_portfolio_invalid_id(self, eclipse_client):
        """Test fetching portfolio with invalid ID returns 404."""
        from orionapi import NotFoundError

        with pytest.raises(NotFoundError):
            eclipse_client.get_portfolio(999999999)

    def test_get_account_details_invalid_id(self, eclipse_client):
        """Test fetching account details with invalid ID returns empty data."""
        # This endpoint returns success with no data for invalid IDs
        result = eclipse_client.get_account_details(999999999)
        # API returns success but with empty or minimal data
        assert result is not None

    def test_get_model_invalid_id(self, eclipse_client):
        """Test fetching model with invalid ID returns 422."""
        from orionapi import OrionAPIError

        with pytest.raises(OrionAPIError, match="Model does not exist"):
            eclipse_client.get_model(999999999)

    def test_get_security_set_invalid_id(self, eclipse_client):
        """Test fetching security set with invalid ID returns empty data."""
        # This endpoint returns success with no data for invalid IDs
        result = eclipse_client.get_security_set(999999999)
        # API returns success but with empty or minimal data
        assert result is not None

    def test_search_securities_no_results(self, eclipse_client):
        """Test searching securities with term that should return no results."""
        results = eclipse_client.search_securities("XYZNONEXISTENTSYMBOL999", top=5)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_all_portfolios_empty_search(self, eclipse_client):
        """Test fetching portfolios with search term that returns no results."""
        filtered = eclipse_client.get_all_portfolios(search="XYZNONEXISTENTPORTFOLIO999")
        assert isinstance(filtered, list)
        # Should return empty list or very few results
        assert len(filtered) == 0 or len(filtered) < 5


class TestOrionAPI:
    def test_check_username(self, orion_client):
        """Test that we can authenticate and get username."""
        username = orion_client.check_username()
        assert username is not None
        assert len(username) > 0

    def test_get_query_payload(self, orion_client, orion_query_id):
        """Test that we can get a query payload."""
        payload = orion_client.get_query_payload(orion_query_id)
        assert isinstance(payload, dict)
        assert "prompts" in payload

    def test_get_query_params(self, orion_client, orion_query_id):
        """Test that we can get query parameters."""
        params = orion_client.get_query_params(orion_query_id)
        assert isinstance(params, list)

    def test_query(self, orion_client, orion_query_id):
        """Test that we can run a query."""
        result = orion_client.query(orion_query_id, {})
        assert isinstance(result, (dict, list))

    def test_get_all_queries(self, orion_client):
        """Test that we can get all custom queries."""
        queries = orion_client.get_all_queries()
        assert isinstance(queries, list)
        # Should have at least some queries available
        if queries:
            assert "id" in queries[0]

    def test_get_all_queries_with_search(self, orion_client):
        """Test getting queries with search filter."""
        # First get all queries to find one to search for
        all_queries = orion_client.get_all_queries()
        if not all_queries:
            pytest.skip("No queries available")

        # Use part of first query name
        search_term = all_queries[0].get("name", "")[:3]
        if not search_term:
            pytest.skip("No query name to search")

        filtered = orion_client.get_all_queries(search_term=search_term)
        assert isinstance(filtered, list)
        # Search should return subset or equal
        assert len(filtered) <= len(all_queries)

    def test_search_queries_returns_rows(self, orion_client):
        """search_queries with a non-empty term returns rows with id and name.

        Note: the underlying endpoint requires a non-empty Search parameter;
        passing "" returns 0 rows from the Orion endpoint.
        """
        queries = orion_client.search_queries(search_term="a", top=10)
        assert isinstance(queries, list)
        if not queries:
            pytest.skip("Tenant has no saved queries matching 'a'")
        assert "id" in queries[0]
        assert "name" in queries[0]

    def test_search_queries_with_term(self, orion_client):
        """search_queries(term) returns rows whose name contains the term."""
        seeds = orion_client.search_queries(search_term="a", top=10)
        if not seeds:
            pytest.skip("Tenant has no saved queries to seed search term")

        term = seeds[0].get("name", "")[:3]
        if not term:
            pytest.skip("Seed query has no usable name prefix")

        filtered = orion_client.search_queries(search_term=term, top=100)
        assert isinstance(filtered, list)
        assert len(filtered) >= 1
        term_lower = term.lower()
        for row in filtered:
            assert term_lower in row.get("name", "").lower()

    def test_search_queries_top_caps_results(self, orion_client):
        """$top caps the result count."""
        queries = orion_client.search_queries(search_term="a", top=2)
        assert isinstance(queries, list)
        assert len(queries) <= 2

    def test_find_query_by_name_exact(self, orion_client):
        """find_query_by_name returns the id for an exact-name match."""
        queries = orion_client.search_queries(search_term="a", top=10)
        if not queries:
            pytest.skip("Tenant has no saved queries")

        target = next((q for q in queries if q.get("name") and q.get("id")), None)
        if target is None:
            pytest.skip("No query has both name and id")

        found_id = orion_client.find_query_by_name(target["name"])
        assert found_id == target["id"]

    def test_find_query_by_name_missing(self, orion_client):
        """find_query_by_name returns None when no query matches."""
        unlikely = "ZZZ_no_such_query_orionapi_test_marker_8290"
        assert orion_client.find_query_by_name(unlikely) is None

    def test_get_query_metadata(self, orion_client, orion_query_id):
        """get_query_metadata returns the record plus a params list."""
        meta = orion_client.get_query_metadata(orion_query_id)
        assert isinstance(meta, dict)
        assert "params" in meta
        assert isinstance(meta["params"], list)
        # params should mirror get_query_params for the same id
        assert meta["params"] == orion_client.get_query_params(orion_query_id)

    # Custom Field Definitions

    def test_get_custom_field_definitions_client(self, orion_client):
        """Test fetching custom field definitions for clients."""
        from orionapi import AuthenticationError, NotFoundError

        try:
            fields = orion_client.get_custom_field_definitions("client")
            assert isinstance(fields, list)
        except (AuthenticationError, NotFoundError):
            pytest.skip("Custom field definitions endpoint not accessible")

    def test_get_custom_field_definitions_account(self, orion_client):
        """Test fetching custom field definitions for accounts."""
        from orionapi import AuthenticationError, NotFoundError

        try:
            fields = orion_client.get_custom_field_definitions("account")
            assert isinstance(fields, list)
        except (AuthenticationError, NotFoundError):
            pytest.skip("Custom field definitions endpoint not accessible")

    # Households (Clients)

    def test_search_clients(self, orion_client):
        """Test searching for clients by name."""
        results = orion_client.search_clients("a", top=5)
        assert isinstance(results, list)

    def test_get_client(self, orion_client):
        """Test fetching a client by ID."""
        results = orion_client.search_clients("a", top=1)
        if not results:
            pytest.skip("No clients found")
        client = orion_client.get_client(results[0]["id"])
        assert isinstance(client, dict)
        assert "id" in client

    def test_get_client_registrations(self, orion_client):
        """Test fetching registrations for a client."""
        results = orion_client.search_clients("a", top=1)
        if not results:
            pytest.skip("No clients found")
        registrations = orion_client.get_client_registrations(results[0]["id"])
        assert isinstance(registrations, list)

    # Registrations

    def test_search_registrations(self, orion_client):
        """Test searching for registrations by name."""
        results = orion_client.search_registrations("a", top=5)
        assert isinstance(results, list)

    def test_get_registration(self, orion_client):
        """Test fetching a registration by ID."""
        results = orion_client.search_registrations("a", top=1)
        if not results:
            pytest.skip("No registrations found")
        registration = orion_client.get_registration(results[0]["id"])
        assert isinstance(registration, dict)
        assert "id" in registration

    def test_get_registration_types(self, orion_client):
        """Test fetching registration types."""
        types = orion_client.get_registration_types()
        assert isinstance(types, list)
        if types:
            assert "id" in types[0]
            assert "name" in types[0]

    # Accounts

    def test_search_orion_accounts(self, orion_client):
        """Test searching for accounts by name."""
        results = orion_client.search_orion_accounts("a", top=5)
        assert isinstance(results, list)

    def test_get_orion_account(self, orion_client):
        """Test fetching an account by ID."""
        results = orion_client.search_orion_accounts("a", top=1)
        if not results:
            pytest.skip("No accounts found")
        account = orion_client.get_orion_account(results[0]["id"])
        assert isinstance(account, dict)
        assert "id" in account

    def test_get_query_params_description(self, orion_client, orion_query_id, capsys):
        """Test printing formatted query parameters."""
        # This method prints to stdout, so we capture it
        orion_client.get_query_params_description(orion_query_id)

        # Verify something was printed
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    # Edge case tests

    def test_get_client_invalid_id(self, orion_client):
        """Test fetching client with invalid ID returns 404."""
        from orionapi import NotFoundError

        with pytest.raises(NotFoundError):
            orion_client.get_client(999999999)

    def test_get_registration_invalid_id(self, orion_client):
        """Test fetching registration with invalid ID returns 500."""
        from orionapi import OrionAPIError

        with pytest.raises(OrionAPIError):
            orion_client.get_registration(999999999)

    def test_get_orion_account_invalid_id(self, orion_client):
        """Test fetching account with invalid ID returns 404."""
        from orionapi import NotFoundError

        with pytest.raises(NotFoundError):
            orion_client.get_orion_account(999999999)

    def test_search_clients_no_results(self, orion_client):
        """Test searching clients with term that should return no results."""
        results = orion_client.search_clients("XYZNONEXISTENTCLIENT999", top=5)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_registrations_no_results(self, orion_client):
        """Test searching registrations with term that should return no results."""
        results = orion_client.search_registrations("XYZNONEXISTENTREG999", top=5)
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_orion_accounts_no_results(self, orion_client):
        """Test searching accounts with term that should return no results."""
        results = orion_client.search_orion_accounts("XYZNONEXISTENTACCT999", top=5)
        assert isinstance(results, list)
        assert len(results) == 0

    # Assets

    def test_get_assets(self, orion_client):
        """Test fetching assets for a specific account."""
        accounts = orion_client.search_orion_accounts("a", top=1)
        if not accounts:
            pytest.skip("No accounts available")

        assets = orion_client.get_assets(accounts[0]["id"])
        assert isinstance(assets, list)

    def test_search_assets(self, orion_client):
        """Test searching for assets by ticker."""
        results = orion_client.search_assets("AAPL", top=5)
        assert isinstance(results, list)

    # Billing

    def test_get_fee_schedules(self, orion_client):
        """Test fetching all fee schedules."""
        schedules = orion_client.get_fee_schedules()
        assert isinstance(schedules, list)

    def test_get_account_billing(self, orion_client):
        """Test fetching billing details for an account."""
        accounts = orion_client.search_orion_accounts("a", top=1)
        if not accounts:
            pytest.skip("No accounts available")

        billing = orion_client.get_account_billing(accounts[0]["id"])
        assert isinstance(billing, dict)

    def test_get_billing_household_summary(self, orion_client):
        """Test fetching billing summary for a household."""
        clients = orion_client.search_clients("a", top=1)
        if not clients:
            pytest.skip("No clients available")

        summary = orion_client.get_billing_household_summary(clients[0]["id"])
        assert isinstance(summary, dict)

    # Reporting

    def test_get_performance_data(self, orion_client):
        """Test fetching performance data for an account."""
        from datetime import datetime, timedelta

        accounts = orion_client.search_orion_accounts("a", top=1)
        if not accounts:
            pytest.skip("No accounts available")

        # Use last 365 days as date range
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

        performance = orion_client.get_performance_data(
            accounts[0]["id"], start_date, end_date, entity_type="account"
        )
        assert isinstance(performance, dict)


class TestEclipse21Endpoints:
    """Live smoke tests for the read/preview methods added in orionapi 2.1.0.

    These fetch real data to confirm the documented endpoints still respond with
    the expected shape — catching upstream route breakage that mocked unit tests
    cannot. Skipped without ECLIPSE_USER/ECLIPSE_PWD.
    """

    def _first_model_id(self, client):
        models = client.get_all_models(top=5)
        if not models:
            pytest.skip("No models available")
        return models[0]["id"]

    def _first_portfolio_id(self, client):
        portfolios = client.get_all_portfolios(top=5)
        if not portfolios:
            pytest.skip("No portfolios available")
        return portfolios[0]["id"]

    # --- no-arg trade-tool / model reference endpoints ---

    def test_get_raise_cash_methods(self, eclipse_client):
        assert isinstance(eclipse_client.get_raise_cash_methods(), list)

    def test_get_spend_cash_methods(self, eclipse_client):
        assert isinstance(eclipse_client.get_spend_cash_methods(), list)

    def test_get_model_status(self, eclipse_client):
        assert isinstance(eclipse_client.get_model_status(), list)

    def test_get_model_types(self, eclipse_client):
        assert isinstance(eclipse_client.get_model_types(), list)

    def test_get_submodels(self, eclipse_client):
        assert isinstance(eclipse_client.get_submodels(), list)

    # --- paged / filtered variants of existing list endpoints ---

    def test_get_all_models_top(self, eclipse_client):
        assert isinstance(eclipse_client.get_all_models(top=3), list)

    def test_get_all_portfolios_top(self, eclipse_client):
        assert isinstance(eclipse_client.get_all_portfolios(top=3), list)

    def test_get_trades_top(self, eclipse_client):
        assert isinstance(eclipse_client.get_trades(top=3), list)

    def test_get_trade_instances_raw(self, eclipse_client):
        from datetime import datetime, timedelta

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        assert isinstance(
            eclipse_client.get_trade_instances(start_date, end_date, normalize=False), list
        )

    # --- model-scoped endpoints ---

    def test_get_model_nodes(self, eclipse_client):
        assert isinstance(
            eclipse_client.get_model_nodes(self._first_model_id(eclipse_client)), dict
        )

    def test_get_model_portfolios(self, eclipse_client):
        assert isinstance(
            eclipse_client.get_model_portfolios(self._first_model_id(eclipse_client)), list
        )

    def test_get_model_pending(self, eclipse_client):
        assert isinstance(
            eclipse_client.get_model_pending(self._first_model_id(eclipse_client)), dict
        )

    def test_get_model_analysis(self, eclipse_client):
        assert isinstance(
            eclipse_client.get_model_analysis(self._first_model_id(eclipse_client)), dict
        )

    def test_get_model_allocations_no_aggregate(self, eclipse_client):
        assert isinstance(
            eclipse_client.get_model_allocations(
                self._first_model_id(eclipse_client), aggregate=False
            ),
            list,
        )

    # --- account / portfolio path variants ---

    def test_get_portfolio_accounts_simple(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.get_portfolio_accounts(pid, simple=True), list)

    def test_get_portfolio_holdings_detail(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.get_portfolio_holdings_detail(pid), list)

    def test_account_simple_holdings_and_taxlots(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        accts = eclipse_client.get_portfolio_accounts(pid, simple=True)
        if not accts:
            pytest.skip("No accounts in portfolio")
        account_id = accts[0]["accountId"]

        assert isinstance(eclipse_client.get_account_simple(account_id), dict)

        holdings = eclipse_client.get_account_holdings_detail(account_id)
        assert isinstance(holdings, list)
        if not holdings:
            pytest.skip("No holdings to source a tax-lot from")
        assert isinstance(eclipse_client.get_taxlots(holdings[0]["id"]), list)

    # --- security sets ---

    def test_get_security_set_summary(self, eclipse_client):
        sets = eclipse_client.get_all_security_sets()
        if not sets:
            pytest.skip("No security sets available")
        assert isinstance(eclipse_client.get_security_set_summary(sets[0]["id"]), dict)

    @pytest.mark.xfail(
        reason="Upstream Eclipse routes /security/securityset/detail into the /{id} "
        "param route, returning 400 'id is not numeric string'. Use get_all_security_sets "
        "+ get_security_set(id). Flips to XPASS if Eclipse fixes the route.",
        strict=False,
    )
    def test_get_security_set_details(self, eclipse_client):
        assert isinstance(eclipse_client.get_security_set_details(), list)


class TestEclipseV2CoverageBatch1:
    """Live smoke tests for the v2-only read methods (coverage batch 1).

    Confirms the documented v2 surface responds with the expected container type.
    Skipped without ECLIPSE_USER/ECLIPSE_PWD. Uses .v2 explicitly.
    """

    def _first_portfolio_id(self, client):
        portfolios = client.v1.get_all_portfolios(top=5)
        if not portfolios:
            pytest.skip("No portfolios available")
        return portfolios[0]["id"]

    # no-arg firm-level reads
    def test_esg_themes(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_esg_themes(), list)

    def test_esg_assignments(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_esg_assignments(), list)

    def test_asset_classification_groups(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_asset_classification_groups(), list)

    def test_asset_classification_methods(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_asset_classification_methods(), list)

    def test_dashboard_fields(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_dashboard_fields(), list)

    def test_astro_all_templates(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_astro_all_templates(), dict)

    def test_analytics_run_config(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_analytics_run_config(), list)

    def test_analytics_banner_status(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_analytics_banner_status(), dict)

    def test_optimization_batch_summary(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_optimization_batch_summary(), list)

    def test_trade_blocks(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_trade_blocks(), list)

    # portfolio-scoped tactical / ESG reads
    def test_tactical_portfolio_summary(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.v2.get_tactical_portfolio_summary(pid), dict)

    def test_tactical_account_cash_detail(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.v2.get_tactical_account_cash_detail(pid), list)

    def test_tactical_tax_lots(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.v2.get_tactical_tax_lots(pid), list)

    def test_tactical_restricted_securities(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.v2.get_tactical_restricted_securities(pid), list)

    def test_esg_restrictions_for_portfolio(self, eclipse_client):
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.v2.get_esg_restrictions_for_portfolio(pid), list)

    def test_unifier_exposes_v2_only_method(self, eclipse_client):
        # v2-only method reachable directly on the unifier (falls through to .v2)
        pid = self._first_portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.get_tactical_portfolio_summary(pid), dict)


class TestEclipseV2CoverageBatch2:
    """Live smoke tests for v2 Trading/TradeInstance reads (coverage batch 2).

    Optimization reads are role-gated (OPTIMIZER) and Notes needs a valid
    relatedType enum, so those are covered by unit tests only.
    """

    def _date_window(self):
        from datetime import datetime, timedelta

        today = datetime.now()
        return (today - timedelta(days=120)).strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")

    def test_trading_instances_by_date_range(self, eclipse_client):
        sd, ed = self._date_window()
        assert isinstance(eclipse_client.v2.get_trading_instances_by_date_range(sd, ed), list)

    def test_trading_instances_for_user(self, eclipse_client):
        sd, ed = self._date_window()
        result = eclipse_client.v2.get_trading_instances_for_user(sd, ed, offset=0, limit=10)
        assert isinstance(result, list)

    def test_trading_instances_with_trades(self, eclipse_client):
        sd, ed = self._date_window()
        result = eclipse_client.v2.get_trading_instances_with_trades(
            start_date=sd, end_date=ed, take=5
        )
        assert isinstance(result, (list, dict))

    def test_trading_active_batch_jobs(self, eclipse_client):
        sd, ed = self._date_window()
        assert isinstance(
            eclipse_client.v2.get_trading_active_batch_jobs(start_date=sd, end_date=ed), list
        )

    def test_trading_instances_paginated_by_portfolio(self, eclipse_client):
        portfolios = eclipse_client.v1.get_all_portfolios(top=1)
        if not portfolios:
            pytest.skip("No portfolios available")
        result = eclipse_client.v2.get_trading_instances_paginated(
            portfolio_id=portfolios[0]["id"], take=5
        )
        # Eclipse returns {"data": [...], "total": N}
        assert isinstance(result, dict)
        assert "data" in result

    def test_trading_instance_trades(self, eclipse_client):
        sd, ed = self._date_window()
        instances = eclipse_client.v2.get_trading_instances_by_date_range(sd, ed)
        if not instances:
            pytest.skip("No trade instances in window")
        inst_id = instances[0].get("id") or instances[0].get("tradeInstanceId")
        if not inst_id:
            pytest.skip("No trade-instance id field found")
        assert isinstance(eclipse_client.v2.get_trading_instance_trades(inst_id), list)


class TestEclipseV2CoverageBatch3:
    """Live smoke tests for v2 account / portfolio / sleeve reads (coverage batch 3).

    Sleeve strategies are role-gated (SLEEVES) and get_preference needs a valid
    preference name, so those are unit-tested only.
    """

    def _account_id(self, client):
        accounts = client.v1.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")
        return accounts[0]["id"]

    def _portfolio_id(self, client):
        portfolios = client.v1.get_all_portfolios(top=1)
        if not portfolios:
            pytest.skip("No portfolios available")
        return portfolios[0]["id"]

    # no-arg
    def test_accessible_account_count(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_accessible_account_count(), int)

    def test_accessible_portfolio_count(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_accessible_portfolio_count(), int)

    def test_user_portfolio_ids(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_user_portfolio_ids(), list)

    def test_sleeve_contribution_methods(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_sleeve_contribution_methods(), list)

    def test_sleeve_distribution_methods(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_sleeve_distribution_methods(), list)

    def test_astro_account_filters(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_astro_account_filters(), list)

    def test_astro_accounts(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_astro_accounts(), list)

    def test_portfolio_search(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_portfolio_search(limit=3), list)

    # account-scoped
    def test_account_cash_details(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_account_cash_details(self._account_id(eclipse_client)), dict
        )

    def test_account_gain_loss_summary(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_account_gain_loss_summary(self._account_id(eclipse_client)),
            dict,
        )

    def test_account_history(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_account_history(self._account_id(eclipse_client)), list
        )

    def test_account_transactions(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_account_transactions(self._account_id(eclipse_client)), list
        )

    def test_sleeve_allocations(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_sleeve_allocations(self._account_id(eclipse_client)), dict
        )

    # portfolio-scoped
    def test_portfolio_allocations(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_portfolio_allocations(self._portfolio_id(eclipse_client)), dict
        )

    def test_portfolio_cash_details(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_portfolio_cash_details(self._portfolio_id(eclipse_client)), dict
        )

    def test_portfolio_gain_loss_summary(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_portfolio_gain_loss_summary(self._portfolio_id(eclipse_client)),
            dict,
        )

    def test_portfolio_mac_history(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_portfolio_mac_history(self._portfolio_id(eclipse_client)), dict
        )

    def test_portfolio_tree(self, eclipse_client):
        pid = self._portfolio_id(eclipse_client)
        assert isinstance(eclipse_client.v2.get_portfolio_tree(portfolio_id=pid), dict)


class TestEclipseV2CoverageBatch4:
    """Live smoke tests for v2 model / modeling / security / lookup reads (batch 4)."""

    def _model_id(self, client):
        models = client.v1.get_all_models(top=5)
        if not models:
            pytest.skip("No models available")
        return models[0]["id"]

    def _security_set_id(self, client):
        sets = client.v1.get_all_security_sets()
        if not sets:
            pytest.skip("No security sets available")
        return sets[0]["id"]

    # no-arg / firm-level
    def test_models_v2(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_models_v2(search="a"), list)

    def test_model_types_v2(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_model_types_v2(), list)

    def test_stress_test_scenarios(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_stress_test_scenarios(), list)

    def test_hidden_levers_durations(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_hidden_levers_durations(), list)

    def test_sma_account_type_restrictions(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_sma_account_type_restrictions(), list)

    def test_get_securities(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_securities(), list)

    def test_security_sets_v2(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_security_sets_v2(), list)

    def test_astro_models(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_astro_models(), list)

    def test_strategist_models(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_strategist_models(), list)

    # model-scoped
    def test_model_levels(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_model_levels(self._model_id(eclipse_client)), list)

    def test_model_analysis_v2(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_model_analysis_v2(self._model_id(eclipse_client)), dict
        )

    def test_model_aggregate_analysis(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_model_aggregate_analysis(self._model_id(eclipse_client)), dict
        )

    def test_model_sync_oc_firms(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_model_sync_oc_firms(self._model_id(eclipse_client)), list
        )

    # securityset-scoped
    def test_security_set_history(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_security_set_history(self._security_set_id(eclipse_client)), list
        )

    def test_security_set_detail_history(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_security_set_detail_history(
                self._security_set_id(eclipse_client)
            ),
            dict,
        )


class TestEclipseV2ConfigPrefs:
    """Live smoke tests for the verifiable config/preference reads (batch 7).

    Money-market / tax-lot preferences need a specific relatedType enum, and
    configuration / feature-flag reads need known IDs, so those plus all writes
    are unit-tested only.
    """

    def test_previous_business_day(self, eclipse_client):
        result = eclipse_client.v2.get_previous_business_day("2026-05-29")
        assert isinstance(result, (str, dict))

    def test_preference_securities(self, eclipse_client):
        portfolios = eclipse_client.v1.get_all_portfolios(top=1)
        if not portfolios:
            pytest.skip("No portfolios available")
        result = eclipse_client.v2.get_preference_securities("Portfolio", portfolios[0]["id"])
        assert isinstance(result, dict)


class TestEclipseV2OrgRefBatch10:
    """Live smoke tests for v2 org/workflow/reference reads (batch 10).

    security_search needs external firm/account context and admin/custodian
    detail + writes need known IDs, so those are unit-tested only.
    """

    def test_firm_types(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_firm_types(), list)

    def test_token_environment(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_token_environment(), (str, dict))

    def test_token_info(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_token_info(), dict)

    def test_execution_destination_types(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_execution_destination_types(), list)

    def test_allocation_instructions(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_allocation_instructions(), list)

    def test_trade_execution_allocation_types(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_trade_execution_allocation_types(), list)

    def test_trade_execution_types(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_trade_execution_types(), list)

    def test_product_classes(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_product_classes(), list)

    def test_risk_categories(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_risk_categories(), list)

    def test_service_teams(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_service_teams(), list)

    def test_service_team(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_service_team(), dict)

    def test_advisor_number(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_advisor_number(), dict)

    def test_get_teams(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_teams(), list)

    def test_firm_logo_base64(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_firm_logo_base64(), dict)

    def test_account_search(self, eclipse_client):
        assert isinstance(eclipse_client.v2.account_search("a", limit=3), list)

    def test_global_search(self, eclipse_client):
        assert isinstance(eclipse_client.v2.global_search(search="a", limit=3), dict)

    def test_workflow_contexts(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_workflow_contexts(), list)

    def test_workflow_tools(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_workflow_tools(), list)

    def test_workflow_mcp_servers(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_workflow_mcp_servers(), list)


class TestEclipseV1ReadCoverageBatch12:
    """Live smoke tests for v1 reference/sub-resource reads (batch 12).

    get_portfolio_account_count 400s upstream (route collision) and get_sleeves
    is role-gated (SLEEVES), so those are unit-tested only.
    """

    def test_account_filters(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_account_filters(), list)

    def test_aside_cash_amount_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_aside_cash_amount_types(), list)

    def test_aside_cash_expiration_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_aside_cash_expiration_types(), list)

    def test_aside_cash_transaction_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_aside_cash_transaction_types(), list)

    def test_restricted_plans(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_restricted_plans(), list)

    def test_holding_filters(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_holding_filters(), list)

    def test_portfolio_filters(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_portfolio_filters(), (list, dict))

    def test_accounts_without_portfolio(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_accounts_without_portfolio(), list)


class TestEclipseV1ReadCoverageBatch13:
    """Live smoke tests for v1 modeling/security reference reads (batch 13).

    submodels_usage 400s upstream (route collision) and model_can_delete returns
    422 for in-use models, so those are unit-tested only.
    """

    def test_model_filter_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_model_filter_types(), list)

    def test_model_management_styles(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_model_management_styles(), list)

    def test_security_statuses(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_security_statuses(), list)

    def test_security_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_security_types(), list)

    def test_corporate_action_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_corporate_action_types(), list)

    def test_security_set_buy_priority(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_security_set_buy_priority(), list)

    def test_security_set_sell_priority(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_security_set_sell_priority(), list)

    def test_security_set_equivalent_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_security_set_equivalent_types(), list)

    def test_model_upload_templates(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_model_upload_templates(), (list, dict))

    def test_model_security_types(self, eclipse_client):
        models = eclipse_client.v1.get_all_models(top=3)
        if not models:
            pytest.skip("No models available")
        assert isinstance(eclipse_client.v1.get_model_security_types(models[0]["id"]), (list, dict))


class TestEclipseCoverageBatch15:
    """Live smoke tests for batch-15 account/portfolio/model/security reads."""

    def _pid(self, c):
        ps = c.v1.get_all_portfolios(top=1)
        if not ps:
            pytest.skip("no portfolios")
        return ps[0]["id"]

    def test_v2_get_accounts(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_accounts(), list)

    def test_v2_get_account(self, eclipse_client):
        accts = eclipse_client.v1.get_all_accounts()
        if not accts:
            pytest.skip("no accounts")
        assert isinstance(eclipse_client.v2.get_account(accts[0]["id"]), dict)

    def test_v2_portfolio_v2(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_portfolio_v2(self._pid(eclipse_client)), dict)

    def test_v2_portfolio_summary(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_portfolio_summary(self._pid(eclipse_client)), dict)

    def test_v2_portfolio_accounts_v2(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_portfolio_accounts_v2(self._pid(eclipse_client)), list
        )

    def test_v2_portfolio_team_history(self, eclipse_client):
        assert isinstance(
            eclipse_client.v2.get_portfolio_team_history(self._pid(eclipse_client)), list
        )

    def test_v2_portfolio_list(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_portfolio_list(limit=3), list)

    def test_v2_securities_by_ticker(self, eclipse_client):
        assert isinstance(eclipse_client.v2.get_securities_by_ticker(["AAPL"]), list)

    def test_v1_aside_cash_account_types(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_aside_cash_account_types(), list)

    def test_v1_model_detail_portfolio_ids(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_model_detail_portfolio_ids(), (list, dict))

    def test_v1_new_account_template(self, eclipse_client):
        assert isinstance(eclipse_client.v1.get_new_account_template(), (list, dict))
