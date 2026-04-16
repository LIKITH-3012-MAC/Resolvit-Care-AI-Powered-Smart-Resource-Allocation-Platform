"""
Resources API — Inventory management
FastAPI Router version.
"""

from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Body, Request
from backend.database import fetch_all, fetch_one, execute_returning, execute

router = APIRouter()

@router.get("")
async def list_resources(
    res_type: Optional[str] = Query(None, alias="type"),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1)
):
    """List resource inventory."""
    conditions = []
    params = []
    idx = 1

    if res_type:
        conditions.append(f"type = ${idx}")
        params.append(res_type)
        idx += 1
    if status:
        conditions.append(f"availability_status = ${idx}")
        params.append(status)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT * FROM resource_inventory
        {where}
        ORDER BY type, name
        LIMIT ${idx}
    """
    params.append(limit)

    rows = await fetch_all(query, *params)
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)
    return {"data": rows, "total": len(rows)}


@router.post("")
async def create_resource(payload: dict = Body(...)):
    """Add a resource to inventory."""
    name = payload.get("name")
    res_type = payload.get("type")
    
    if not name or not res_type:
        raise HTTPException(status_code=400, detail="name and type required")
        
    row = await execute_returning(
        """INSERT INTO resource_inventory
           (name, type, quantity, unit, warehouse_location,
            warehouse_latitude, warehouse_longitude)
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           RETURNING *""",
        name, res_type, payload.get("quantity", 0),
        payload.get("unit", "units"), payload.get("warehouse_location", ""),
        payload.get("warehouse_latitude"), payload.get("warehouse_longitude")
    )
    return {"data": row, "message": "Resource added"}


@router.patch("/{resource_id}")
async def update_resource(resource_id: str, payload: dict = Body(...)):
    """Update resource quantity or status."""
    quantity = payload.get("quantity")
    status = payload.get("status")

    fields = []
    params = []
    idx = 1

    if quantity is not None:
        fields.append(f"quantity = ${idx}")
        params.append(quantity)
        idx += 1
    if status:
        fields.append(f"availability_status = ${idx}")
        params.append(status)
        idx += 1

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(resource_id)
    query = f"UPDATE resource_inventory SET {', '.join(fields)} WHERE id = ${idx} RETURNING *"
    row = await execute_returning(query, *params)
    
    if not row:
         raise HTTPException(status_code=404, detail="Resource not found")

    return {"data": row, "message": "Resource updated"}


@router.get("/summary")
async def resource_summary():
    """Get resource inventory summary by type."""
    rows = await fetch_all(
        """SELECT type,
                   COUNT(*) as item_count,
                   SUM(quantity) as total_quantity,
                   SUM(CASE WHEN availability_status = 'available' THEN quantity ELSE 0 END) as available_qty
            FROM resource_inventory
            GROUP BY type
            ORDER BY type"""
    )
    return {"data": rows}
