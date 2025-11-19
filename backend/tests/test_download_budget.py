import pytest
import io
import pandas as pd
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_download_budget_with_buffer(async_client: AsyncClient):
    """Test download budget when buffer exists"""
    from backend.main import app  # ✅ Fixed import
    
    df = pd.DataFrame({
        "Category": ["Groceries & Shopping"],
        "Budget_Amount": [10000],
        "Forecasted_Amount": [9500]
    })
    
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    app.state.budget_stream = buffer
    
    response = await async_client.post("/download/budget")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.mark.asyncio
async def test_download_budget_no_buffer(async_client: AsyncClient):
    """Test download budget when no buffer exists"""
    from backend.main import app  # ✅ Fixed import
    
    if hasattr(app.state, "budget_stream"):
        app.state.budget_stream = None
    
    response = await async_client.post("/download/budget")
    
    assert response.status_code == 200
    data = response.json()
    assert "error" in data