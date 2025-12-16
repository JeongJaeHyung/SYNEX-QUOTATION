from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_detailed_quotation():
    """
    Detailed Quotation API endpoint.
    """
    return {"message": "Detailed Quotation API - Empty content for now."}
