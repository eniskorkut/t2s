---
name: fastapi-expert
description: Definitive guide for building high-performance, async APIs with FastAPI, Pydantic v2, and Vanna integration.
---

# FastAPI Expert Guidelines

This skill defines the coding standards for the `t2s` project backend. We prioritize **Performance**, **Type Safety**, and **Clean Architecture**.

## 1. 🏗️ Architecture: Service-Repository Pattern

Do NOT write business logic inside routes (endpoints). Keep controllers thin.

* **❌ BAD (Logic in Router):**
    ```python
    @app.get("/users")
    async def get_users():
        # DB connection code here...
        # SQL query string here...
        return data
    ```

* **✅ GOOD (Separation of Concerns):**
    * `api/routes/` -> Handles HTTP Request/Response, status codes.
    * `services/` -> Contains business logic (e.g., Calling Vanna, calculating stats).
    * `models/` -> Pydantic schemas (Data Transfer Objects).

    ```python
    @router.post("/generate", response_model=QueryResponse)
    async def generate_sql_endpoint(
        request: QueryRequest,
        service: ChatService = Depends(get_chat_service)
    ):
        # Delegate to service layer
        return await service.process_question(request.question)
    ```

## 2. ⚡ Asynchronous First

Since we are doing I/O bound operations (Database, LLM API calls), **everything must be async**.

* Always use `async def` for route handlers.
* Always use `await` when calling Vanna functions (wrap them if they are blocking).
* **Tip:** If Vanna's `run_sql` is blocking, run it in a threadpool using `run_in_threadpool`.

## 3. 🛡️ Data Validation (Pydantic V2)

Strictly define what comes IN and what goes OUT.

* **Input Schemas:** Use specific models (e.g., `QuestionCreate`).
* **Output Schemas:** Don't return raw DB objects or Tuples; return Pydantic models.
* **Config:** Use `model_config = ConfigDict(from_attributes=True)` for ORM compatibility.

## 4. 💉 Dependency Injection

Never manually instantiate services or DB connections inside a route. Use FastAPI's `Depends`.

```python
from fastapi import Depends
from api.dependencies import get_db

async def get_chat_service(db = Depends(get_db)):
    return ChatService(db)