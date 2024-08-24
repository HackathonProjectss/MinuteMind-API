from fastapi import HTTPException, status
class ItemsService:
    @staticmethod
    def get_items():
        return {"items": ["item1", "item2", "item3"]}
    
    @staticmethod
    def get_item(item_id: int):
        if item_id == 1:
            return {"item_id": item_id, "name": "item1"}
        elif item_id == 2:
            return {"item_id": item_id, "name": "item2"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
        
    @staticmethod
    def create_item(item: dict):
        return item
    
    @staticmethod
    def update_item(item_id: int, item: dict):
        return {"item_id": item_id, **item}