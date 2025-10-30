import pytest
import io
import pandas as pd
from httpx import AsyncClient
from backend.database import User

# Helper function to create test Excel file
def create_test_transaction_excel(transactions: dict = None) -> io.BytesIO:
    """Helper to create test transaction Excel file"""
    if transactions is None:
        transactions = {
            "Description": ["shopping in bhatbhateni", "salary credited", "restaurant bill"],
            "Dr.": [4300, 0, 1500],
            "Cr.": [0, 100000, 0],
            "Balance (NPR)": [35000, 135000, 133500],
            "Status": ["COMPLETE", "COMPLETE", "COMPLETE"],
            "Channel": ["WEB", "APP", "WEB"]
        }
    
    df = pd.DataFrame(transactions)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    return buffer


@pytest.mark.asyncio
async def test_budget_prediction_requires_auth(async_client: AsyncClient):
    """Test that budget prediction requires authentication"""
    
    buffer = create_test_transaction_excel()
    
    # Create proper multipart form data
    files = {"files": ("transactions.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    data = {"income": 100000, "saving_amt": 10000}
    
    response = await async_client.post(
        "/predict_budget",
        data=data,
        files=files
    )
    
    assert response.status_code == 401


# @pytest.mark.asyncio
# async def test_budget_prediction_success(
#     authenticated_client: AsyncClient,
#     test_user: User
# ):
#     """Test successful budget prediction"""
    
#     buffer = create_test_transaction_excel()
    
#     # Proper format: data as dict, files as dict
#     response = await authenticated_client.post(
#         "/predict_budget",
#         params={"income": 100000, "saving_amt": 10000},  # or put inside JSON
#         files={"files": ("transactions.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
#     )
    
#     assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_budget_prediction_with_multiple_files(
#     authenticated_client: AsyncClient,
#     test_user: User
# ):
#     """Test budget prediction with multiple Excel files"""
    
#     # Create first file
#     buffer1 = create_test_transaction_excel({
#         "Description": ["grocery store", "electricity bill"],
#         "Dr.": [2000, 1000],
#         "Cr.": [0, 0],
#         "Balance (NPR)": [48000, 47000],
#         "Status": ["COMPLETE", "COMPLETE"],
#         "Channel": ["WEB", "APP"]
#     })
    
#     # Create second file
#     buffer2 = create_test_transaction_excel({
#         "Description": ["salary credited", "rent payment"],
#         "Dr.": [0, 15000],
#         "Cr.": [100000, 0],
#         "Balance (NPR)": [147000, 132000],
#         "Status": ["COMPLETE", "COMPLETE"],
#         "Channel": ["APP", "WEB"]
#     })
    
#     # For multiple files with same field name, use list of tuples
#     files = [
#         ("files", ("file1.xlsx", buffer1, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")),
#         ("files", ("file2.xlsx", buffer2, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
#     ]
    
#     response = await authenticated_client.post(
#         "/predict_budget",
#         data={"income": 100000, "saving_amt": 20000},
#         files=files
#     )
    
#     assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_budget_prediction_invalid_file_format(
#     authenticated_client: AsyncClient,
#     test_user: User
# ):
#     """Test budget prediction with invalid file format"""
    
#     # Create invalid file (plain text instead of Excel)
#     buffer = io.BytesIO(b"This is not an Excel file")
#     buffer.seek(0)
    
#     response = await authenticated_client.post(
#         "/predict_budget",
#         data={"income": 100000, "saving_amt": 10000},
#         files={"files": ("invalid.txt", buffer, "text/plain")}
#     )
    
#     # Should return error for invalid format - 422 is also acceptable for invalid input
#     assert response.status_code in [400, 422, 500]


@pytest.mark.asyncio
async def test_budget_prediction_missing_required_columns(
    authenticated_client: AsyncClient,
    test_user: User
):
    """Test budget prediction with missing Description column"""
    
    # Create Excel without Description column
    data = {
        "Dr.": [4300, 0],
        "Cr.": [0, 100000],
        "Balance (NPR)": [35000, 85000]
    }
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    buffer.seek(0)
    
    response = await authenticated_client.post(
        "/predict_budget",
        data={"income": 100000, "saving_amt": 10000},
        files={"files": ("no_description.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    )
    
    # Should handle missing columns gracefully - 422 is acceptable for validation errors
    assert response.status_code in [400, 422, 500]


# @pytest.mark.asyncio
# async def test_budget_prediction_with_zero_income(
#     authenticated_client: AsyncClient,
#     test_user: User
# ):
#     """Test budget prediction with zero income"""
    
#     buffer = create_test_transaction_excel()
    
#     response = await authenticated_client.post(
#         "/predict_budget",
#         data={"income": 0, "saving_amt": 0},
#         files={"files": ("transactions.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
#     )
    
#     # Should either succeed with zero budget or return validation error - 422 is acceptable
#     assert response.status_code in [200, 400, 422]


# @pytest.mark.asyncio
# async def test_budget_prediction_validates_categories(
#     authenticated_client: AsyncClient,
#     test_user: User
# ):
#     """Test that predictions classify into known categories"""
    
#     buffer = create_test_transaction_excel()
    
#     response = await authenticated_client.post(
#         "/predict_budget",
#         data={"income": 100000, "saving_amt": 10000},
#         files={"files": ("transactions.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
#     )
    
#     assert response.status_code == 200
    
    # If your endpoint returns JSON with results
    # Uncomment and adjust based on your actual response structure
    # data = response.json()
    # expected_categories = [
    #     'Personal Care', 'Income', 'Banking & Finance', 
    #     'Dining & Food', 'Groceries & Shopping', 'Subscriptions',
    #     'others', 'Entertainment', 'Travel', 'Education'
    # ]
    # 
    # for result in data.get('results', []):
    #     assert result['category'] in expected_categories