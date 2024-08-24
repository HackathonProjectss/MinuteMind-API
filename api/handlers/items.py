from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer
from services.items import ItemsService

items_router = APIRouter()

@items_router.get("/", summary="List all items")
async def list_items():
    return ItemsService.get_items()

@items_router.get("/{item_id}", summary="Get an item by ID")
async def get_item(item_id: int):
    return ItemsService.get_item(item_id)
    
@items_router.post("/", summary="Create a new item")
async def create_item(item: dict):
    return ItemsService.create_item(item)

@items_router.put("/{item_id}", summary="Update an item by ID")
async def update_item(item_id: int, item: dict):
    return ItemsService.update_item(item_id, item)