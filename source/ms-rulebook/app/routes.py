from fastapi import APIRouter, HTTPException, status
import logging

from app.db import create_rule, list_rules, get_rule, update_rule, delete_rule
from app.models import RuleCreate, RuleUpdate, RuleResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/rules", tags=["Rules"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RuleResponse)
async def create_new_rule(body: RuleCreate) -> dict:
    try:
        rule = await create_rule(body.model_dump())
        logger.info(f"Created rule {rule['id']}")
        return rule
    except ValueError as e:
        logger.warning(f"Validation error creating rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating rule: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create rule: {str(e)}"
        )


@router.get("/", response_model=list[RuleResponse])
async def list_all_rules() -> list[dict]:
    try:
        rules = await list_rules()
        logger.info(f"Retrieved {len(rules)} rules")
        return rules
    except Exception as e:
        logger.error(f"Error listing rules: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rules: {str(e)}"
        )


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_single_rule(rule_id: str) -> dict:
    try:
        rule = await get_rule(rule_id)
        if rule is None:
            raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rule: {str(e)}"
        )


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_existing_rule(rule_id: str, body: RuleUpdate) -> dict:
    try:
        rule = await update_rule(rule_id, body.model_dump())
        if rule is None:
            raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
        logger.info(f"Updated rule {rule_id}")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update rule: {str(e)}"
        )


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_rule(rule_id: str) -> None:
    try:
        deleted = await delete_rule(rule_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
        logger.info(f"Deleted rule {rule_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting rule {rule_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete rule: {str(e)}"
        )
