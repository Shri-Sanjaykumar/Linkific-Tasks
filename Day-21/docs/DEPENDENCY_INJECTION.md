# Day 21 — Modular Dependency Injection System

## 1. Overview & Advantages of Dependency Injection

Dependency Injection (DI) is a core design pattern in FastAPI powered by `Depends()`. Rather than having endpoint functions directly instantiate services, read environment variables, parse headers, or query databases, dependencies are declared as function parameters and resolved automatically by the framework.

### Primary Advantages:
1. **Decoupled Architecture:** Endpoints depend on abstract contracts rather than concrete implementations.
2. **Reusability (DRY):** Common logic (such as authentication, pagination, and request telemetry) is written once and shared across dozens of routes.
3. **Effortless Test Mocking:** Tests can replace real services or authentication checks with mock objects via `app.dependency_overrides` without touching endpoint code.
4. **Hierarchical Composition:** Dependencies can themselves depend on other sub-dependencies (e.g. `require_admin_role` depends on `verify_api_key`).

---

## 2. Implemented Dependencies in Day 21

### 2.1 Request Context Dependency (`get_request_context`)
Extracts caller metadata into a structured `RequestContext` object:
- Correlation ID (`request.state.request_id`)
- Client IP address (`request.client.host`)
- Sanitized `User-Agent` (truncated to 200 chars)
- HTTP method and path

```python
def get_request_context(request: Request) -> RequestContext:
    request_id = getattr(request.state, "request_id", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    return RequestContext(request_id=request_id, client_ip=client_ip, ...)
```

### 2.2 Security & Role Authorization (`verify_api_key` & `require_admin_role`)
Enforces header-based authentication with strict 401 vs 403 status code semantics:

| Situation | Status Code | Error Code | Reason |
| :--- | :---: | :--- | :--- |
| Missing `X-API-Key` header | **401** | `UNAUTHORIZED` | Client must supply credentials to access protected resource. |
| Invalid `X-API-Key` value | **401** | `UNAUTHORIZED` | Secret does not match configured keys (evaluated in constant time using `hmac.compare_digest`). |
| Valid standard key on admin route | **403** | `FORBIDDEN` | Caller is authenticated, but lacks administrative role. |
| Valid admin key on admin route | **200** | `OK` | Request proceeds normally. |

### 2.3 Bounded Pagination Dependency (`get_pagination`)
Protects against unbounded database/file queries and SQL injection attempts:
- `skip >= 0` (rejects negative numbers with HTTP 422)
- `1 <= limit <= 100` (rejects oversized requests with HTTP 422)
- `order_by` validated against strict allowlist `{'timestamp', 'duration', 'status'}`.

### 2.4 Service Dependency (`get_async_service`)
Provides a shared singleton instance of `AsyncDataService`.

---

## 3. Test Overrides in PyTest

FastAPI's dependency injection allows instantaneous mocking in test environments without global state pollution:

```python
def test_dependency_override_in_tests(client):
    from app.dependencies import verify_api_key
    from app.main import app

    # Temporarily override authentication for unit testing
    app.dependency_overrides[verify_api_key] = lambda: {"role": "test_mock_role", "user": "test_user"}

    try:
        response = client.post("/api/v1/query", json={"question": "Testing override"})
        assert response.status_code == 200
    finally:
        # Guarantee cleanup
        app.dependency_overrides.clear()
```
