import pytest
from httpx import AsyncClient
from backend.database import User

@pytest.mark.asyncio
async def test_login_valid_with_fixture(async_client: AsyncClient, test_user: User):
    """Test login with user created by fixture"""
    response = await async_client.post(
        "/auth/token",  
        data={  
            "username": test_user.username, 
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_json_endpoint(async_client: AsyncClient, test_user: User):
    """Test login using JSON endpoint"""
    response = await async_client.post(
        "/auth/login",
        json={  
            "username": test_user.username,
            "password": "testpassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"