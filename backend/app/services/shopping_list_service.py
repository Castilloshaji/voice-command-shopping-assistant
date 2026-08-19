from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.shopping_list import ListItem
from app.models.history import ShoppingHistory
from app.schemas.shopping_list import ListItemCreate, ListItemUpdate
from app.services.categorization_service import CategorizationService

class ShoppingListService:
    @staticmethod
    def get_all_items(db: Session) -> List[ListItem]:
        """Retrieve all shopping list items ordered by ID."""
        return db.query(ListItem).order_by(ListItem.id.asc()).all()

    @staticmethod
    def get_item_by_id(db: Session, item_id: int) -> Optional[ListItem]:
        """Retrieve a single shopping list item by ID."""
        return db.query(ListItem).filter(ListItem.id == item_id).first()

    @staticmethod
    def create_item(db: Session, item_data: ListItemCreate) -> ListItem:
        """
        Create a shopping list item or merge quantity into an active duplicate.
        - First matches against Product catalog and categorizes item.
        - Checks for active (is_completed == False) item by product_id or normalized item_name.
        - Increments quantity if active item exists; creates new item if completed or absent.
        """
        product_id, category = CategorizationService.match_product_and_category(db, item_data.item_name)
        clean_name = item_data.item_name.strip().lower()

        # Step A: Match active uncompleted item by product_id
        active_item = None
        if product_id is not None:
            active_item = db.query(ListItem).filter(
                ListItem.is_completed == False,
                ListItem.product_id == product_id
            ).first()

        # Step B: If no product_id match, match by normalized item_name
        if not active_item:
            active_item = db.query(ListItem).filter(
                ListItem.is_completed == False,
                func.lower(ListItem.item_name) == clean_name
            ).first()

        # If active duplicate exists, increment quantity
        if active_item:
            active_item.quantity += item_data.quantity
            if item_data.unit:
                active_item.unit = item_data.unit
            db.commit()
            db.refresh(active_item)
            return active_item

        # Otherwise create new ListItem
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
        - Allowed fields: quantity, unit, is_completed.
        - Records ShoppingHistory purchase event ONLY when is_completed transitions False -> True.
        """
        item = db.query(ListItem).filter(ListItem.id == item_id).first()
        if not item:
            return None

        old_is_completed = item.is_completed
        update_fields = item_data.model_dump(exclude_unset=True)

        for key, value in update_fields.items():
            setattr(item, key, value)

        # Record ShoppingHistory purchase event if transitioning from False -> True
        if item_data.is_completed is True and old_is_completed is False:
            history_event = ShoppingHistory(
                item_name=item.item_name,
                category=item.category,
                quantity=item.quantity
            )
            db.add(history_event)

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

    @staticmethod
    def clear_list(db: Session) -> int:
        """Removes all items from shopping list. Returns count of deleted items."""
        count = db.query(ListItem).delete()
        db.commit()
        return count
