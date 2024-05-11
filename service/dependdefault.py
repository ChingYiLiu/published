import yaml
import logging
import datetime
import pytz
from typing import Union
FORMAT = '%(asctime)s [%(levelname)s]: %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)
from fastapi import Request
import re
import os
import numpy as np
import requests
from requests.exceptions import ConnectionError
import asyncio


# config
def get_myconfig(_myconfig_file):
    ## read custom params from config.yaml
    with open(_myconfig_file, 'r', encoding="utf-8") as stream:
        _myconfig = yaml.load(stream, Loader=yaml.CLoader)
    return _myconfig

myconfig = get_myconfig("service/config/config.yml")
db_site = "service/db_data/guest_list.db"

#%% DB related
import pandas as pd
import sqlite3
from typing import Tuple
import time
def select_db(_sql:str = '', _api_name:str='', request_id:int = 0) -> Tuple[pd.DataFrame, float]:
    _df = pd.DataFrame()
    time_start = time.time()
    try:
        the_conn = sqlite3.connect(db_site)
        cur = the_conn.cursor()
        cur.execute(_sql)
        _data = cur.fetchall()
        if len(_data) > 0:
            col_names = [col[0].lower() for col in cur.description]
            _df = pd.DataFrame(columns = col_names, data = _data)
        process_time =  time.time()-time_start
        _log_info = f'db connected process time = {process_time}'
        logging.info(_log_info)
    except Exception as e:
        _error_info = f'error call from {_api_name} | errror message: {e}, sql: {_sql}'
        logging.error(_error_info)
    finally:
        the_conn.close()

    return _df

def upload_db(sql: str , df_db: pd.DataFrame = None, truncate_sql = '', _api_name:str='', request_id:int = 0):
    """
    if df_db is None --> execute sql dirrectly.
    """
    connection = sqlite3.connect(db_site)
    cur = connection.cursor()

    ## delete old data
    if len(truncate_sql) >0:
        ##Truncate Table tgifriday.items_web_crawler_price
        try:
            cur.execute(truncate_sql)
        except Exception as e:
            cur.close()
            connection.close()
            logging.error(e)
            return
        logging.info('truncate old data : done')
    
    ## insert new data
    # sql = '''insert into member_info (name, phone_number, birth_date, group_id, created_at, updated_dt)
    #         values (?,?,?,?,?,?)
    # '''
    df_list = df_db.values.tolist()
    batch_size = 10000
    data = []
    try:
        if df_db is None:
            cur.execute(sql)
        else:
            for i in df_list: 
                data.append(i)
                if len(data) % batch_size == 0:
                    cur.executemany(sql, data)
                    connection.commit()
                    data = []
            if data:
                cur.executemany(sql, data)
        connection.commit()
        logging.info( "Successfully Update Latest Data!")
        error_flag = 0
    except Exception as e:
        logging.error(e)
        error_flag = 1
    finally:
        cur.close()
        connection.close()
    return error_flag
