#%%
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import random
from service.api.api_router import router as api_router
#from pydantic import BaseSettings
from pydantic_settings import BaseSettings
import logging
import datetime
import pytz

#%%
from fastapi import FastAPI, Request, HTTPException

class Settings(BaseSettings):
    openapi_url: str = ""
settings = Settings()
# app = FastAPI(openapi_url=settings.openapi_url)
app = FastAPI()

# 這些是固定的
app.include_router(api_router)


#%% CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


import time
@app.middleware("http")
async def log_request(request: Request, call_next):

    request.state.request_timestamp = datetime.datetime.now(pytz.timezone('Asia/Taipei'))

    request_id = random.randint(100000000,999999999)
    request.state.request_id = request_id

    try: #有踩到request.client不存在的狀況 --2023/11/7 
        x_forwarded_for: Optional[str] = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            remote_ip = x_forwarded_for.split(',')[0]
        else:
            remote_ip = request.client.host
    except:
        remote_ip = '--'
    request.state.remote_ip = remote_ip

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f'remote_ip={remote_ip}, process_time={process_time} sec')    
    return response

@app.on_event("startup")
async def startup():
    # init shared_data
    # thread job

    # other startup function
    logging.info('Hi~~~~~~~~~~~~')
    pass

@app.on_event("shutdown")
def app_shutdown():
    logging.info('Bye~~~~~~~~~~~')
    pass

#%%
from fastapi.responses import Response
@app.get("/favicon.ico", include_in_schema=False)
async def disable_favicon():
    pass

# add ping (service level)
@app.get("/ping", summary="Check that the service is operational")
def pong():
    if False: # 這裡應該有一個 service level 的判斷
        raise HTTPException(status_code=403, detail="NOO") 
    else:
        return {"ping": "ping!"}