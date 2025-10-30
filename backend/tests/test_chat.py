import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_general_chat_without_auth(async_client: AsyncClient):
    """
    Test general chat endpoint without authentication.
    Should respond with intent = 'general' for simple finance-related queries.
    """

    response = await async_client.post(
        "/chat",
        json={"text": "What is a finance?"}
    )

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Body: {response.text}"

    data = response.json()
    assert "intent" in data, "Missing 'intent' key in response"
    assert "response" in data, "Missing 'response' key in response"

    # Validate correct intent & meaningful answer
    assert data["intent"] == "general", f"Expected 'general', got {data['intent']}"
    assert len(data["response"].strip()) > 10, "Response seems too short"
    print(f"✅ Response: {data['response'][:150]}...")


@pytest.mark.asyncio
async def test_general_chat_returns_helpful_response(async_client: AsyncClient):
    """
    Test that general chat returns a meaningful response for budgeting question.
    """

    response = await async_client.post(
        "/chat",
        json={"text": "what is a bank?"}
    )

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}. Body: {response.text}"

    data = response.json()
    assert "intent" in data and "response" in data, "Incomplete response JSON"
    assert data["intent"] == "general", f"Expected 'general', got {data['intent']}"

    text = data["response"].lower()
    assert len(text) > 50, "Response too short to be meaningful"
    # Note: Depending on your knowledge base, adjust these assertions
    # assert "budget" in text or "finance" in text, "Response doesn't mention budget-related terms"

    print(f"✅ Chat Response (truncated): {data['response'][:200]}...")