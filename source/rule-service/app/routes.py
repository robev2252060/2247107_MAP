from fastapi import APIRouter, HTTPException, status

from app.db import create_rule, list_rules, get_rule, update_rule, delete_rule
from app.models import RuleCreate, RuleUpdate

router = APIRouter(prefix="/rules", tags=["Rules"])


@router.get("/", summary="List all automation rules")
async def list_all_rules() -> list[dict]:
    return await list_rules()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new automation rule")
async def create_new_rule(body: RuleCreate) -> dict:
    return await create_rule(body.model_dump())


@router.get("/{rule_id}", summary="Get a single rule by ID")
async def get_single_rule(rule_id: str) -> dict:
    rule = await get_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
    return rule


@router.patch("/{rule_id}", summary="Partially update a rule")
async def patch_rule(rule_id: str, body: RuleUpdate) -> dict:
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    rule = await update_rule(rule_id, updates)
    if rule is None:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a rule")
async def remove_rule(rule_id: str) -> None:
    deleted = await delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
