from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.shopping_list import ListItem
from app.schemas.intent import ParsedIntent, IntentEnum
from app.schemas.command import CommandExecutionResponse
from app.schemas.shopping_list import ListItemCreate, ListItemUpdate, ListItemResponse
from app.schemas.product import ProductResponse
from app.services.shopping_list_service import ShoppingListService
from app.services.product_service import ProductService
from app.services.recommendation_service import RecommendationService

class CommandService:
    @staticmethod
    def execute_command(db: Session, parsed: ParsedIntent) -> CommandExecutionResponse:
        """
        Orchestrates intent execution by dispatching ParsedIntent to the appropriate domain service.
        """
        intent = parsed.intent

        # 1. ADD_ITEM
        if intent == IntentEnum.ADD_ITEM:
            if not parsed.item:
                return CommandExecutionResponse(
                    success=False,
                    intent=intent,
                    message="Item name is required for addition.",
                    data=None
                )
            
            qty = parsed.quantity if parsed.quantity is not None else 1.0
            unit = parsed.unit

            # Check if active item existed prior to creation for clear messaging
            clean_item_name = parsed.item.strip().lower()
            existed_active = db.query(ListItem).filter(
                ListItem.is_completed == False,
                func.lower(ListItem.item_name) == clean_item_name
            ).first()

            item_obj = ShoppingListService.create_item(
                db,
                ListItemCreate(item_name=parsed.item, quantity=qty, unit=unit)
            )

            unit_str = f" {item_obj.unit}" if item_obj.unit else ""
            if existed_active:
                msg = f"Updated '{item_obj.item_name}' quantity to {item_obj.quantity}{unit_str} on your shopping list."
            else:
                msg = f"Added {item_obj.quantity}{unit_str} '{item_obj.item_name}' to your shopping list."

            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=msg,
                data=ListItemResponse.model_validate(item_obj).model_dump(mode="json")
            )

        # 2. REMOVE_ITEM
        if intent == IntentEnum.REMOVE_ITEM:
            if not parsed.item:
                return CommandExecutionResponse(
                    success=False,
                    intent=intent,
                    message="Item name is required for removal.",
                    data=None
                )

            clean_target = parsed.item.strip().lower()
            # Match active item first, fallback to any item
            target_item = db.query(ListItem).filter(
                ListItem.is_completed == False,
                func.lower(ListItem.item_name) == clean_target
            ).first()

            if not target_item:
                target_item = db.query(ListItem).filter(
                    func.lower(ListItem.item_name) == clean_target
                ).first()

            if not target_item:
                return CommandExecutionResponse(
                    success=False,
                    intent=intent,
                    message=f"'{parsed.item}' is not on your shopping list.",
                    data=None
                )

            deleted_name = target_item.item_name
            ShoppingListService.delete_item(db, target_item.id)

            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=f"Removed '{deleted_name}' from your shopping list.",
                data={"removed_item_id": target_item.id}
            )

        # 3. UPDATE_QUANTITY
        if intent == IntentEnum.UPDATE_QUANTITY:
            if not parsed.item or parsed.quantity is None:
                return CommandExecutionResponse(
                    success=False,
                    intent=intent,
                    message="Item name and quantity are required for updating.",
                    data=None
                )

            clean_target = parsed.item.strip().lower()
            target_item = db.query(ListItem).filter(
                ListItem.is_completed == False,
                func.lower(ListItem.item_name) == clean_target
            ).first()

            if not target_item:
                return CommandExecutionResponse(
                    success=False,
                    intent=intent,
                    message=f"'{parsed.item}' is not on your shopping list.",
                    data=None
                )

            updated = ShoppingListService.update_item(
                db,
                target_item.id,
                ListItemUpdate(quantity=parsed.quantity, unit=parsed.unit)
            )

            unit_str = f" {updated.unit}" if updated.unit else ""
            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=f"Updated '{updated.item_name}' quantity to {updated.quantity}{unit_str}.",
                data=ListItemResponse.model_validate(updated).model_dump(mode="json")
            )

        # 4. SHOW_LIST
        if intent == IntentEnum.SHOW_LIST:
            items = ShoppingListService.get_all_items(db)
            data_items = [ListItemResponse.model_validate(i).model_dump(mode="json") for i in items]
            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=f"Retrieved {len(items)} items from your shopping list.",
                data=data_items
            )

        # 5. CLEAR_LIST
        if intent == IntentEnum.CLEAR_LIST:
            count = ShoppingListService.clear_list(db)
            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=f"Cleared all {count} items from your shopping list.",
                data={"deleted_count": count}
            )

        # 6. SEARCH_PRODUCT
        if intent == IntentEnum.SEARCH_PRODUCT:
            products = ProductService.search_products(
                db,
                query=parsed.item,
                brand=parsed.brand,
                min_price=parsed.min_price,
                max_price=parsed.max_price
            )
            data_prods = [ProductResponse.model_validate(p).model_dump(mode="json") for p in products]
            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=f"Found {len(products)} matching products in catalog.",
                data=data_prods
            )

        # 7. GET_SUGGESTIONS
        if intent == IntentEnum.GET_SUGGESTIONS:
            suggestions = RecommendationService.get_suggestions(db, limit=5)
            data_suggs = [s.model_dump(mode="json") for s in suggestions]
            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=f"Generated {len(suggestions)} shopping suggestions.",
                data=data_suggs
            )

        # 8. UNKNOWN / AMBIGUOUS
        return CommandExecutionResponse(
            success=False,
            intent=IntentEnum.UNKNOWN,
            message="I couldn't understand that command.",
            data=None
        )
