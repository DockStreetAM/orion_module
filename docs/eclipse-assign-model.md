# Eclipse — Assign a Model to an Existing Portfolio (`assignModel`)

**Status:** endpoint + request DTO verified live against the prod Eclipse tenant
(2026-07-07, via throwaway empty test portfolios that were created and deleted).
Documents the mechanism for a `update_portfolio_model` write tool (DeeSam #395).

## Problem

`create_portfolio` accepts `modelId` only **at creation**. There was no documented
way to change the model on an **existing** portfolio. The Eclipse REST API does
support it, but the request body shape is undocumented in the `orionapi` client
(the method's docstring just says "Model-assignment DTO").

## Endpoint

```
PUT {base_url_v2}/Portfolio/Portfolios/action/assignModel
```

`orionapi` client method (top-level `Eclipse` → routes to V2):

```python
Eclipse.assign_model_to_portfolios(payload)   # does: api_request(url, requests.put, json=payload)
```

## Request body — a JSON ARRAY, not an object

The body **is** a JSON array of `PortfolioModelAssignment` objects. Wrapping it in
an object (`{"modelId":…, "portfolioIds":[…]}`, `{"assignments":[…]}`, etc.) fails:

```
400 Bad Request
{'errors': {'modelId': ["Cannot deserialize the current JSON object … into type
'ICollection<OAS.Eclipse.Entities.Firm.Portfolio.PortfolioModelAssignment>'
because the type requires a JSON array (e.g. [1,2,3]) …"]}}
```

**Confirmed working shape (→ 200 OK):**

```json
[
  { "portfolioId": 519, "modelId": 6 }
]
```

```python
client.assign_model_to_portfolios([{"portfolioId": pid, "modelId": model_id}])
```

Multiple portfolios can presumably be assigned in one call (the array is a
collection) — not exercised here; assume `[{portfolioId, modelId}, …]`.

## Verifying the assignment

The assigned model surfaces in the **`general`** block of `GET
/Portfolio/Portfolios/{id}` (`Eclipse.get_portfolio`), not at the top level:

```json
"general": {
  "modelId": 6,
  "modelName": "100% Equities",
  "substitutedModelId": null,
  "pendingApprovalModelId": null,
  "pendingApprovalModelName": null
}
```

After the `assignModel` call on an empty portfolio: `modelId`/`modelName` were set
immediately and `pendingApprovalModelId` was **null** — i.e. the assignment took
effect directly; it did **not** enqueue an Eclipse-side pending-approval, and (on
an empty portfolio) triggered no rebalance/trades. `pendingApprovalModelId` /
`substitutedModelId` exist in the schema — worth checking on a *funded* portfolio,
where model changes may behave differently (drift → rebalance).

## Gotchas found while probing (client/auth)

- Eclipse auth = Basic (Orion creds) → session JWT via the `orionapi` `Eclipse`
  client. Reads work firm-wide (243 portfolios visible for the trade-ops account).
- **`get_teams()` returns `[]`** for the trade-ops account, even though teams
  exist. Read a team id from the `teams[]` block on any full portfolio record
  instead — the firm's **Default Team = id 1**. `create_portfolio` needs
  `{"name", "teamIds":[1], "primaryTeamId":1}`.
- **Model list** is `Eclipse.get_all_models(name=…, top=…)` (EclipseV1). The
  top-level `Eclipse.__getattr__` routes bare `get_models` to V2, which raises
  `AttributeError` — use `get_all_models`.
- `delete_portfolio(id)` → `DELETE /portfolio/portfolios/{id}` works and fully
  removes a test portfolio (used for cleanup).

## Recommended tool (DeeSam #395)

`update_portfolio_model(portfolio_id: int, model_id: int)` in the
**eclipse-readwrite-notrade** tier, **approval-gated**, assignment-only:

```python
client.assign_model_to_portfolios([{"portfolioId": portfolio_id, "modelId": model_id}])
```

- Gate it (real-money-adjacent) via the existing `gate_or_submit` → `_exec_*` →
  `_WRITE_DISPATCH` pattern; the exec must NOT be `@mcp.tool()`-decorated.
- No auto-rebalance at the firm, so assignment-only is safe; still confirm behavior
  on a **funded** portfolio before first real use (does assign flip `needAnalytics`
  / create pending trades?).
- Return the post-assignment `general.modelId`/`modelName` as the approver's proof.
