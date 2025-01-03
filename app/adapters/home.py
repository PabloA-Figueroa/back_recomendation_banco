# -*- coding: utf-8 -*-
from fastapi import  APIRouter, HTTPException
from data.database.mysql import MySqlConnection
router = APIRouter()

@router.get("/get/personal_maps")
async def get_personal_maps():
    try:
        db = MySqlConnection()
        personal_info = db.get_all_personal_info()
        return {
            "status": "200",
            "data": personal_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))