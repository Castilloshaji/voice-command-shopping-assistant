from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.shopping_list import ListItemCreate, ListItemUpdate, ListItemResponse
from app.services.shopping_list_service import ShoppingListService

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("", response_model=List[ListItemResponse], status_code=status.HTTP_200_OK)
def get_items(db: Session = Depends(get_db)):
    """Retrieve all shopping list items."""
    return ShoppingListService.get_all_items(db)

@router.post("", response_model=ListItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item_data: ListItemCreate,
    db: Session = Depends(get_db)
):
    """Add a new item to the shopping list with automatic product matching and categorization."""
    try:
        return ShoppingListService.create_item(db, item_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create shopping list item."
        )

@router.put("/{item_id}", response_model=ListItemResponse, status_code=status.HTTP_200_OK)
def update_item(
    item_id: int = Path(..., gt=0, description="The ID of the item to update"),
    item_data: ListItemUpdate = ...,
    db: Session = Depends(get_db)
):
    """Update quantity, unit, or completion status of an existing item."""
    updated_item = ShoppingListService.update_item(db, item_id, item_data)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return updated_item

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_item(
    item_id: int = Path(..., gt=0, description="The ID of the item to delete"),
    db: Session = Depends(get_db)
):
    """Remove an item from the shopping list."""
    success = ShoppingListService.delete_item(db, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found"
        )
    return {"message": "Item deleted successfully", "id": item_id}
