import pytest
import io
import pandas as pd
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_download_classification_with_buffer(async_client: AsyncClient):
    """Test download classification when buffer exists in app state"""
    from backend.main import app  # ✅ Fixed import
    
    buffer = io.BytesIO()
    buffer.write(b"Fake Excel Data")
    buffer.seek(0)
    app.state.txn_stream = buffer
    
    response = await async_client.post("/download/classification")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.mark.asyncio
async def test_download_classification_no_buffer(async_client: AsyncClient):
    """Test download classification when no buffer exists"""
    from backend.main import app  # ✅ Fixed import
    
    if hasattr(app.state, "txn_stream"):
        app.state.txn_stream = None
    
    response = await async_client.post("/download/classification")
    
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_download_classification_with_real_excel(async_client: AsyncClient):
    """Test download with actual Excel data"""
    from backend.main import app  # ✅ Fixed import
    
    df = pd.DataFrame({
        "text": ["Shopping at mall", "Salary credited"],
        "category": ["Groceries & Shopping", "Income"],
        "confidence": ["0.95", "0.98"]
    })
    
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    
    app.state.txn_stream = buffer
    
    response = await async_client.post("/download/classification")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.mark.asyncio
async def test_download_classification_multiple_times(async_client: AsyncClient):
    """Test that download can only happen once (buffer is cleared)"""
    from backend.main import app  # ✅ Fixed import
    
    buffer = io.BytesIO()
    buffer.write(b"Test Excel Data")
    buffer.seek(0)
    app.state.txn_stream = buffer
    
    # First download should succeed
    response1 = await async_client.post("/download/classification")
    assert response1.status_code == 200
    
    # Second download should fail (buffer cleared)
    response2 = await async_client.post("/download/classification")
    assert response2.status_code == 200
    data = response2.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_download_classification_buffer_content_integrity(async_client: AsyncClient):
    """Test that downloaded content matches uploaded content"""
    from backend.main import app  # ✅ Fixed import
    
    original_df = pd.DataFrame({
        "Description": ["Test transaction 1", "Test transaction 2"],
        "Category": ["Dining & Food", "Travel"],
        "Amount": [500, 1000]
    })
    
    buffer = io.BytesIO()
    original_df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    
    app.state.txn_stream = buffer
    
    response = await async_client.post("/download/classification")
    
    assert response.status_code == 200
    
    # Verify content
    downloaded_buffer = io.BytesIO(response.content)
    downloaded_df = pd.read_excel(downloaded_buffer, engine='openpyxl')
    
    assert len(downloaded_df) == len(original_df)
    assert list(downloaded_df.columns) == list(original_df.columns)