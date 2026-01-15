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
        portfolio_id = accounts[0].get('portfolioId')
        if not portfolio_id:
            pytest.skip("No portfolio ID found in accounts")

        portfolio = eclipse_client.get_portfolio(portfolio_id)
        assert 'general' in portfolio
        assert 'portfolioName' in portfolio['general']

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
            assert 'id' in portfolios[0]

    def test_get_portfolio_accounts(self, eclipse_client):
        """Test that we can fetch accounts for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]['id']
        accounts = eclipse_client.get_portfolio_accounts(portfolio_id)
        assert isinstance(accounts, list)

    def test_get_portfolio_holdings(self, eclipse_client):
        """Test that we can fetch holdings for a portfolio."""
        portfolios = eclipse_client.get_all_portfolios()
        if not portfolios:
            pytest.skip("No portfolios available")

        portfolio_id = portfolios[0]['id']
        holdings = eclipse_client.get_portfolio_holdings(portfolio_id)
        assert isinstance(holdings, list)

    def test_get_account_holdings(self, eclipse_client):
        """Test that we can fetch holdings for an account."""
        accounts = eclipse_client.get_all_accounts()
        if not accounts:
            pytest.skip("No accounts available")

        account_id = accounts[0]['id']
        holdings = eclipse_client.get_account_holdings(account_id)
        assert isinstance(holdings, list)
