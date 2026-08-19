from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.shopping_list import ListItem
from app.schemas.shopping_list import ListItemCreate, ListItemUpdate
from app.services.categorization_service import CategorizationService

class ShoppingListService:
    @staticmethod
    def get_all_items(db: Session) -> List[ListItem]:
        """Retrieve all shopping list items ordered by creation date."""
        return db.query(ListItem).order_by(ListItem.id.asc()).all()

    @staticmethod
    def get_item_by_id(db: Session, item_id: int) -> Optional[ListItem]:
        """Retrieve a single shopping list item by ID."""
        return db.query(ListItem).filter(ListItem.id == item_id).first()

    @staticmethod
    def create_item(db: Session, item_data: ListItemCreate) -> ListItem:
        """
        Create a shopping list item.
        Automatically matches item against Product catalog and categorizes it.
        """
        product_id, category = CategorizationService.match_product_and_category(db, item_data.item_name)
        
        new_item = ListItem(
            item_name=item_data.item_name,
            quantity=item_data.quantity,
            unit=item_data.unit,
            product_id=product_id,
            category=category,
            is_completed=False
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    @staticmethod
    def update_item(db: Session, item_id: int, item_data: ListItemUpdate) -> Optional[ListItem]:
        """
        Update an existing shopping list item.
        Allowed fields: quantity, unit, is_completed.
        """
        item = db.query(ListItem).filter(ListItem.id == item_id).first()
        if not item:
            return None

        update_fields = item_data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            setattr(item, key, value)

        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def delete_item(db: Session, item_id: int) -> bool:
        """Delete a shopping list item by ID."""
        item = db.query(ListItem).filter(ListItem.id == item_id).first()
        if not item:
            return False

        db.delete(item)
        db.commit()
        return True
