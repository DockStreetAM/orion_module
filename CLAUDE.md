# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python wrapper for the Orion Advisor and Eclipse trading platform APIs. Provides two main classes:
- `OrionAPI` - Interface for Orion Advisor API (reporting, custom queries)
- `EclipseAPI` - Interface for Eclipse trading platform (accounts, orders, models, trade tools)
## Goal
To provide an easy to use python wrapper for the api where the user can supply username and password and get the mostly frequently used endpoints. Complexity ay be hidden (endpoints and parameters rarely used)

## Commands

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run a single test
poetry run pytest tests/test_orion_module.py::TestBasics::test_version
```

## Version Management

Version must be updated in two places when releasing:
- `orionapi/__init__.py` (`__version__`)
- `pyproject.toml` (`version`)

GitHub Actions are triggered by new releases. To release:
1. Bump version in both files
2. Commit and push
3. Create release with `gh release create vX.Y.Z --title "vX.Y.Z"`

## Architecture

Single module in `orionapi/__init__.py` containing both API classes.

### API Pattern

Both classes follow the same pattern:
- Constructor accepts credentials and auto-logs in
- `api_request()` method handles authenticated requests with session token
- Methods return `.json()` parsed responses
- POST requests pass `requests.post` as `req_func` parameter to `api_request()`

### EclipseAPI Authentication

Supports two auth methods:
- Username/password: `EclipseAPI(usr="user", pwd="pass")`
- Orion token exchange: `EclipseAPI(orion_token="token")`

### Account ID Resolution

Eclipse uses internal IDs. Use `get_internal_account_id()` or `search_accounts_number_and_name()` to resolve custodian account numbers to internal IDs.

## API Documentation

- Orion API: https://api.orionadvisor.com/api/v1/
- Eclipse API: https://api.orioneclipse.com/doc/ (requires auth)
- Developer Portal: https://developers.orionadvisor.com/
