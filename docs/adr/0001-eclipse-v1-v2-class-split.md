# ADR 0001 — Split EclipseAPI into explicit v1 / v2 classes with a unifying "best of both" class

- **Status:** Accepted — implemented in 2.0.0
- **Date:** 2026-05-30
- **Deciders:** Spencer Ogden
- **Supersedes:** the single mixed `EclipseAPI` class (v1 methods + one v2 method)

> **Implementation note (2.0.0):** Shipped as `EclipseBase` → `EclipseV1` / `EclipseV2`,
> plus `Eclipse` (composition unifier: shared token, `.v1`/`.v2`, `__getattr__`-delegates
> the v1 long tail to `self.v1`, overrides `get_set_asides` to `self.v2`). `EclipseAPI` is
> a `DeprecationWarning` subclass of `Eclipse`. The unifier uses `__getattr__` forwarding
> rather than hand-listing ~60 delegations — a deliberate, lower-maintenance realization of
> the "pure composition" decision (still composition; `.v1`/`.v2` remain explicit).

## Context

The Orion Eclipse platform exposes **two parallel HTTP surfaces on the same host**:

- **v1** — `https://api.orioneclipse.com/v1/...` — the stable backbone. Mostly simple
  GETs. The wrapper's 26 existing Eclipse methods all target v1.
- **v2** — `https://api.orioneclipse.com/api/v2/...` — a newer, broader surface
  (~400 paths / 58 resource groups) built for newer Eclipse UI features. Often
  **POST-with-body / batch** semantics. **Not a version successor** to v1 — the two
  coexist; Orion has not deprecated v1.

  > Gotcha (already fixed, see `eclipse-v2-host-root-misleading-403` skill): v2 lives at
  > the **host root** (`/api/v2`), NOT under `/v1`. Building v2 URLs off the v1 base
  > yields an unroutable path that Eclipse answers with a misleading
  > `403 "...privileges...undefined"`.

As of v1.11.0 the wrapper is 96% v1 (26 methods) with exactly one v2 method
(`get_set_asides`, which the v2 batch endpoint serves strictly better — firm-wide in one
call, natively carrying the set-aside `id` and `accountNumber`). That single mixed class
hides *which* surface a call hits, which is the opposite of what we want as v2 adoption grows.

### v2 coverage of the current v1 surface (from `EclipseV2Swagger.json`)

| Wrapper v1 area | v2 equivalent exists? |
|---|---|
| Account list **and detail** (`/account/accounts/simple`, `/{id}`) | ✅ `GET /api/v2/Account/Accounts`, `…/{accountId}`, `POST …/list` |
| Portfolio list / search / cash | ✅ `Portfolio/Portfolios/*` |
| Models (`/modeling/models`) | ✅ `Model/GetAllModels`, `Modeling/*` |
| Security sets (`/security/securityset`) | ✅ `SecuritySet/*` |
| Trade orders (`/tradeorder/*`) | ✅ `TradeOrder/*` (extensive) |
| Analytics status / run (`/dataimport/...`) | ✅ `Analytics/*` (different shape) |
| **Holdings** (`/holding/holdings/simple`) | ❌ **v1-only** (only Optimization/OptionTrading holding views in v2) |
| **Authorization / user** (`check_username`) | ❌ **v1-only** (v2 exposes only OAuth endpoints) |

**Conclusion:** "everything on v2" is **not possible** — holdings and auth/user have no
v2 equivalent. v1 remains the backbone. v2 is adopted per-endpoint where it is *strictly
better*.

## Decision

Restructure the Eclipse client into an explicit class hierarchy. **Users should always
know which API version they are hitting.**

```
BaseAPI                      # existing: api_request, RateLimiter, log sanitizing, SSL
  └─ EclipseBase             # NEW shared base
       ├─ EclipseV1          # NEW — every /v1 endpoint, explicit
       ├─ EclipseV2          # NEW — /api/v2 endpoints, explicit
       └─ (composition) Eclipse   # NEW — best-of-both unifier
```

### `EclipseBase(BaseAPI)` — shared base

- Eclipse auth/login: username/password → `GET /v1/admin/token`, and Orion-token exchange.
  (Auth is shared; the same Session JWT authorizes both surfaces.)
- `base_url` (`…/v1`) and `base_url_v2` (`…/api/v2`).
- `_get_auth_header`, token lock, rate limiter (inherited).
- **Account-id resolution helpers** live here (`get_internal_account_id`,
  `search_accounts`, `normalize_name`, `search_accounts_number_and_name`) because some
  **v2 operations require a v1 lookup** (the v2 set-aside batch needs internal account
  ids, sourced from the v1 `/account/accounts/simple` search). Putting them in the base
  lets `EclipseV2` reuse them without duplicating v1 logic.
- **Generic escape hatch:**
  ```python
  def eclipse_request(self, path, version="v1", method="get", **kwargs):
      """Call any Eclipse endpoint on either surface. Explicit, not a fallback.
      version='v1' -> base_url; version='v2' -> base_url_v2. Returns parsed JSON."""
  ```
  This makes the ~400-path v2 long tail reachable without hand-wrapping each one.

### `EclipseV1(EclipseBase)`

All 26 current Eclipse methods, unchanged behavior, explicitly v1. This is a
near-mechanical move of today's `EclipseAPI` method bodies. `get_set_asides` here is the
**per-account v1** form (`GET /account/accounts/{id}/asidecash`).

### `EclipseV2(EclipseBase)`

v2 endpoints, explicitly v2. Seeds with what we've verified:
- `get_set_asides(account_id=None, active_only=False)` — the v2 batch
  `POST /api/v2/Account/Accounts/SetAsideCashSettings` (current 1.11.0 behavior).
- A starter set of high-value, verified-present endpoints (accounts list/detail, models,
  security sets, trade orders, analytics) added incrementally.
- Everything else reachable via `eclipse_request(..., version="v2")`.

### `Eclipse` — unifier (pure composition)

- Holds `self.v1 = EclipseV1(...)` and `self.v2 = EclipseV2(...)`, **sharing one token**
  (authenticate once, inject the token into both — do not log in twice).
- Exposes `.v1` and `.v2` for explicit access, so the version is always discoverable.
- Delegates a **curated** method set to whichever surface is best; each unifier method's
  docstring names the surface it uses. Default to v1 (complete); use v2 only where it
  wins (e.g. `get_set_asides` → v2 batch). Holdings / `check_username` → always v1.
- Mechanism: explicit delegation methods (not inheritance — avoids MRO collisions when
  both subclasses define the same name). A `__getattr__` forward to `self.v1` for the
  v1 long tail MAY be used to cut boilerplate, decided at implementation time.

### `EclipseAPI` — deprecated alias

`EclipseAPI` becomes a thin subclass/alias of `Eclipse` that emits a
`DeprecationWarning` on construction and preserves today's public surface **including the
v2 `get_set_asides` behavior** shipped in 1.11.0. Kept for one or two releases, then
removed.

## Versioning

This ships as **2.0.0**. Importing `EclipseAPI` keeps working (deprecated alias), and its
behavior is preserved, so the break is limited to: the canonical class names change, and
consumers are nudged toward `EclipseV1` / `EclipseV2` / `Eclipse`.

## Migration plan (phased)

1. **2.0.0 — structural split (no behavior change for `EclipseAPI` users):**
   `EclipseBase` (incl. `eclipse_request`), `EclipseV1` (move current methods),
   `EclipseV2` (set-asides + escape hatch), `Eclipse` (composition unifier),
   `EclipseAPI` deprecated alias. Tests reorganized per class; full suite stays green.
2. **2.x — grow `EclipseV2`** with verified high-value endpoints (accounts, models,
   security sets, trade orders, analytics), each validated live like set-asides.
3. **2.x — enrich the unifier** to prefer v2 where measurably better; document the choice
   per method.
4. **3.0.0 — remove the `EclipseAPI` alias** once consumers have migrated.

## Consequences

**Positive**
- Users always know which surface they're calling (explicit classes + `.v1`/`.v2`).
- Clean home for the v1↔v2 coupling (account resolution in the base).
- The escape hatch unlocks the entire v2 surface immediately, cheaply.
- The unifier captures "best of both" without hiding it.

**Negative / risks**
- Larger class surface and more tests to maintain (three classes + unifier).
- The unifier must re-expose v1's methods (composition boilerplate, or `__getattr__`).
- Holdings and auth/user are permanently v1; "all v2" is off the table — the unifier must
  encode those exceptions.
- Migrating a method to v2 changes its return shape (different field names, batch/POST);
  each such move is a deliberate, documented breaking change for that method.

## References
- `EclipseV2Swagger.json` (OpenAPI 3.0.1, ~400 v2 paths).
- Skill `eclipse-v2-host-root-misleading-403` (v2 base-URL gotcha).
- Shipped precedent: `get_set_asides` v2 batch (orionapi 1.11.0).
