import pandas as pd
import asyncio
from fastapi import APIRouter, Request
from service.dependdefault import select_db
import time

router = APIRouter()

#%%
@router.get("/get_by_name")
async def get_by_name(name:str, request:Request):
    request_id = request.state.request_id
    name = name.lower()

    if '萬生' in name and len(name) <= 3:
        return '你是新郎吧！？裝什麼賓客 >_^'

    sql = f"""
        select *
        from guest_list
        where name like '%{name}%'
    """
    df_db= select_db(_sql=sql, _api_name="get_by_name", request_id=request_id )

    if len(df_db) > 1:
        name_getted = df_db.name.tolist()
        name_getted = "、".join(name_getted)
        return f'唉呀，有點模糊的稱呼呢... 請問您是 {name_getted} 其中的哪一位呢？'
    elif len(df_db) == 1:
        name_getted = df_db.name.values[0]
        attend_info = df_db.attend_info.values[0]
        return f'親愛的{name_getted}，已幫您登記「{attend_info}」。'
    else:
        return '再試試看、或者請儘快聯繫 萬生/璟儀 確認唷！' 