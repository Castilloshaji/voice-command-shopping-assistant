from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.shopping_list import ListItem
from app.schemas.intent import ParsedIntent, IntentEnum, IntentItem
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
            target_items: List[IntentItem] = []
            if parsed.items:
                target_items = parsed.items
            elif parsed.item:
                target_items = [IntentItem(
                    item=parsed.item,
                    quantity=parsed.quantity if parsed.quantity is not None else 1.0,
                    unit=parsed.unit
                )]

            if not target_items:
                return CommandExecutionResponse(
                    success=False,
                    intent=intent,
                    message="Item name is required for addition.",
                    data=None
                )

            # Attempt catalog-aware compound segmentation for any target item that cannot be resolved directly
            expanded_target_items: List[IntentItem] = []
            for item_info in target_items:
                single_res = ProductService.resolve_product(db, item_info.item)
                if single_res["exact_match"] is None:
                    segmented = ProductService.resolve_compound_items(
                        db,
                        item_info.item,
                        initial_qty=item_info.quantity,
                        initial_unit=item_info.unit
                    )
                    if segmented:
                        expanded_target_items.extend(segmented)
                    else:
                        expanded_target_items.append(item_info)
                else:
                    expanded_target_items.append(item_info)

            target_items = expanded_target_items

            # Validate ALL target_items against Product catalog before creating any items
            unrecognized_items = []
            all_suggestions = []

            is_ambiguous_query = False
            for item_info in target_items:
                res = ProductService.resolve_product(db, item_info.item)
                if res["exact_match"] is None:
                    unrecognized_items.append(item_info.item)
                    if res.get("is_ambiguous", False):
                        is_ambiguous_query = True
                    for s in res["suggestions"]:
                        if s.id not in [s_item["product_id"] for s_item in all_suggestions]:
                            all_suggestions.append({"product_id": s.id, "name": s.name})

            # If ANY item is unrecognized: create NOTHING and return clarification error response
            if unrecognized_items:
                bad_item = unrecognized_items[0]
                if is_ambiguous_query and all_suggestions:
                    s_names = [f"'{s['name']}'" for s in all_suggestions[:2]]
                    joined_s = " or ".join(s_names)
                    msg = f"I found several matches for '{bad_item}'. Did you mean {joined_s}?"
                elif all_suggestions:
                    if len(all_suggestions) == 1:
                        s_name = all_suggestions[0]["name"]
                        msg = f"I couldn't identify all the products in that command. Did you mean '{s_name}'?"
                    else:
                        s_names = [f"'{s['name']}'" for s in all_suggestions[:2]]
                        joined_s = " or ".join(s_names)
                        msg = f"I couldn't identify all the products in that command. Did you mean {joined_s}?"
                else:
                    msg = f"I couldn't find '{bad_item}' in our store catalog. Nothing was added."

                return CommandExecutionResponse(
                    success=False,
                    intent=intent,
                    message=msg,
                    data={
                        "unrecognized_items": unrecognized_items,
                        "suggestions": all_suggestions
                    }
                )

            # Single item execution - preserve exact messaging & data format for single item tests
            if len(target_items) == 1:
                item_info = target_items[0]
                qty = item_info.quantity if item_info.quantity is not None else 1.0
                unit = item_info.unit

                clean_item_name = item_info.item.strip().lower()
                existed_active = db.query(ListItem).filter(
                    ListItem.is_completed == False,
                    func.lower(ListItem.item_name) == clean_item_name
                ).first()

                item_obj = ShoppingListService.create_item(
                    db,
                    ListItemCreate(item_name=item_info.item, quantity=qty, unit=unit)
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

            # Compound items execution (multiple additions)
            created_objects = []
            item_phrases = []

            for item_info in target_items:
                qty = item_info.quantity if item_info.quantity is not None else 1.0
                unit = item_info.unit

                item_obj = ShoppingListService.create_item(
                    db,
                    ListItemCreate(item_name=item_info.item, quantity=qty, unit=unit)
                )
                created_objects.append(item_obj)

                # Build phrase for message
                if qty != 1.0 or unit:
                    unit_str = f" {unit}" if unit else ""
                    qty_str = f"{int(qty)}" if qty.is_integer() else f"{qty}"
                    item_phrases.append(f"{qty_str}{unit_str} of {item_obj.item_name}" if unit else f"{qty_str} {item_obj.item_name}")
                else:
                    item_phrases.append(item_obj.item_name)

            if len(item_phrases) == 2:
                joined_phrases = " and ".join(item_phrases)
            else:
                joined_phrases = ", ".join(item_phrases[:-1]) + f", and {item_phrases[-1]}"

            msg = f"Added {joined_phrases} to your shopping list."
            data_list = [ListItemResponse.model_validate(obj).model_dump(mode="json") for obj in created_objects]

            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=msg,
                data=data_list
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
                category=parsed.category,
                brand=parsed.brand,
                min_price=parsed.min_price,
                max_price=parsed.max_price
            )

            if not products:
                return CommandExecutionResponse(
                    success=True,
                    intent=intent,
                    message="No products found matching your search criteria.",
                    data=[]
                )

            data_prods = []
            unavail_count = 0
            sub_count = 0

            for p in products:
                prod_resp = ProductResponse.model_validate(p)
                if not p.is_available:
                    unavail_count += 1
                    sub_objs = ProductService.get_substitutes_for_product(db, p)
                    if sub_objs:
                        sub_count += len(sub_objs)
                        prod_resp.substitute_products = [ProductResponse.model_validate(sub) for sub in sub_objs]
                data_prods.append(prod_resp.model_dump(mode="json"))

            msg = f"Found {len(products)} matching product(s)."
            if unavail_count > 0:
                if sub_count > 0:
                    msg += f" Note: {unavail_count} product(s) unavailable; {sub_count} substitute(s) suggested."
                else:
                    msg += f" Note: {unavail_count} product(s) currently unavailable."

            return CommandExecutionResponse(
                success=True,
                intent=intent,
                message=msg,
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
