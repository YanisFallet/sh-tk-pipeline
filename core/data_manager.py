import os
import sqlite3
from pathlib import Path
from random import randint
from datetime import datetime, timedelta
from logging_config import logger

def sql_connect(relativ_path_to_database : str):
    def wrapper1(func):
        def wrapper2(*args, **kwargs):
            with sqlite3.connect(relativ_path_to_database) as conn:
                cursor = conn.cursor()
                return func(cursor,*args, **kwargs)
        return wrapper2
    return wrapper1

#Database Management of contents

@sql_connect('data/database.db')
def create_table_contents(cursor : sqlite3.Cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_content (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            source_platform TEXT NOT NULL,
            source_account TEXT NOT NULL,
            dist_platform TEXT,
            dist_account TEXT,
            pool TEXT,
            role TEXT NOT NULL,
            filepath TEXT NOT NULL,
            id_filename TEXT NOT NULL,
            schedule TIMESTAMP,
            description TEXT,
            tags TEXT,
            is_corrupted BOOLEAN NOT NULL DEFAULT 0,
            linked_to INTEGER NOT NULL DEFAULT 0,
            is_processed BOOLEAN NOT NULL DEFAULT 0,
            is_published BOOLEAN NOT NULL DEFAULT 0
        );
    """)
        
@sql_connect('data/database.db')
def insert_content_data(cursor : sqlite3.Cursor, source_platform : str, source_account : str, dist_platform : str,
                        dist_account : str , pool : str, role : str,  filepath : str, filename : str,
                        description :str, tags : str, is_published : bool = False):
    cursor.execute("""
        INSERT INTO data_content (source_platform, source_account, dist_platform, dist_account, pool, role, filepath, id_filename, description, tags, is_published)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (source_platform, source_account, dist_platform, dist_account, pool, role, filepath, filename, description, tags, is_published))
        
@sql_connect('data/database.db')
def randomized_schedule_by_dist(cursor : sqlite3.Cursor, dist):
    videos_by_dist = cursor.execute("SELECT id, schedule FROM data_content WHERE dist_account = ?", (dist,)).fetchall()
    for i in videos_by_dist:
        cursor.execute("UPDATE data_content SET schedule = ? WHERE id = ?", (videos_by_dist[randint(0, len(videos_by_dist))][1], i[0]))

@sql_connect('data/database.db')
def randomized_schedule_all(cursor : sqlite3.Cursor):
    dists = cursor.execute("SELECT DISTINCT dist_account FROM data_content").fetchall()
    for dist in dists: 
        randomized_schedule_by_dist(cursor, dist[0])
        
        
@sql_connect('data/database.db')
def get_stat_by_dist(cursor : sqlite3.Cursor):
    return (cursor.execute("""SELECT dist_account, COUNT(*) FROM data_content WHERE is_published = 0 GROUP BY dist""").fetchall(),
            cursor.execute("""SELECT dist_account, COUNT(*) FROM data_content WHERE is_published = 1 GROUP BY dist""").fetchall())

@sql_connect('data/database.db')
def select_id_filename_by_src(cursor : sqlite3.Cursor, src_account : str, src_platform : str, for_dist_platform : str, role : str = "content"):
    if role == 'content':
        return list(set([d[0] for d in cursor.execute(f"SELECT id_filename FROM data_content WHERE source_account = '{src_account}' AND source_platform = '{src_platform}' AND dist_platform = '{for_dist_platform}' AND role = 'content'").fetchall()]))
    else :
        return list(set([d[0] for d in cursor.execute(f"SELECT id_filename FROM data_content WHERE source_account = '{src_account}' AND source_platform = '{src_platform}' AND dist_platform is NULL AND role = 'pool'").fetchall()]))


#Database Management of sources

@sql_connect('data/update_src.db')
def create_table_update_src(cursor : sqlite3.Cursor):
    cursor.execute(""" CREATE TABLE IF NOT EXISTS src_update(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        src TEXT NOT NULL,
        platform TEXT NOT NULL,
        updated_time TIMESTAMP NOT NULL,
        updated_counter INTEGER NOT NULL
    )""")
    

@sql_connect('data/update_src.db')
def update_one_src(cursor : sqlite3.Cursor, src_account, platform):
    selection = cursor.execute(f"SELECT src, updated_counter FROM src_update WHERE src = '{src_account}' AND platform = '{platform}' ").fetchone()
    if selection is None:
        cursor.execute(f"""INSERT INTO src_update (src, platform, updated_time, updated_counter)
                       VALUES(?, ?, ?, ?)""", (src_account, platform, datetime.now(), 1))
    else :
        cursor.execute(f"UPDATE src_update SET updated_counter = '{selection[1] + 1}', updated_time = '{datetime.now()}' WHERE src = '{src_account}' AND platform = '{platform}' ")


@sql_connect('data/update_src.db')
@sql_connect('data/update_pools.db')
def update_src_is_bottom_useless(cursor_pools : sqlite3.Cursor, cursor_database : sqlite3.Cursor, src_account : str, role : str = "content", limit_of_days=30, useless=3) -> tuple[bool, bool]:
    if role == 'content':
        up = cursor_database.execute(f"SELECT updated_time FROM src_update WHERE src = '{src_account}'").fetchone()
    elif role == 'pool':
        up = cursor_pools.execute(f"SELECT updated_time FROM pool_update WHERE src = '{src_account}'").fetchone()
    else:
        raise ValueError("Invalid database specified")
    if up is None:
        return True, False
    else:
        updated_time = datetime.strptime(up[0], '%Y-%m-%d %H:%M:%S.%f').timestamp()
        if (datetime.now() - datetime.fromtimestamp(updated_time)) < timedelta(days=useless):
            return False, True
        elif (datetime.now() - datetime.fromtimestamp(updated_time)) > timedelta(days=limit_of_days):
            return True, False
        else:
            return False, False

#Database Management of dist

@sql_connect('data/update_dist.db')
def create_table_update_dist(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS dist_update(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        dist TEXT NOT NULL,
        platform TEXT  NOT NULL,
        total_contents_published INTEGER DEFAULT 0,
        last_video_uploaded TIMESTAMP,
        updated_time TIMESTAMP,
        daily_upload INTEGER,
        limit_date_for_daily TIMESTAMP
    )""")

@sql_connect('data/update_dist.db')
def update_one_dist(cursor : sqlite3.Cursor, dist_account : str, platform : str):
    selection = cursor.execute(f"SELECT dist, total_contents_published FROM dist_update WHERE dist  = '{dist_account}' AND platform = '{platform}'").fetchone()
    if selection is None:
        cursor.execute(f"INSERT INTO dist_update VALUES({dist_account}, {platform}, 0, {datetime.now()}, {datetime.now()})")
    else :
        cursor.execute(f"UPDATE dist_update SET total_contents_published = '{selection[1] + 1}', updated_time = '{datetime.now()}' WHERE dist = '{dist_account}' AND platform = '{platform}' ")

    
@sql_connect('data/update_dist.db')    
def is_uploadable(cursor : sqlite3.Cursor, dist_account : str, platform : str, count : bool = True, MAX_UPLOAD_DAILY : int = 15, edge : int = 10):
    data_dist =  cursor.execute(f"SELECT * FROM dist_update WHERE dist = '{dist_account}' AND platform = '{platform}'").fetchone()
    if data_dist is None:
        c = 1 if count else 0
        cursor.execute(f"INSERT INTO dist_update (dist, platform, updated_time, daily_upload, limit_date_for_daily) VALUES('{dist_account}', '{platform}', '{datetime.now()}', '{c}', '{datetime.now() + timedelta(days = 1, minutes = edge)}')")
        logger.info(f"{__name__} :  Dist '{dist_account}' on '{platform}' has {MAX_UPLOAD_DAILY - c} upload(s) left")
        return True
    else:
        date_limit = datetime.strptime(data_dist[-1], '%Y-%m-%d %H:%M:%S.%f')
        nbr_daily_upload = data_dist[-2]
        if datetime.now() < date_limit:
            if nbr_daily_upload < MAX_UPLOAD_DAILY:
                if count:
                    logger.info(f"{__name__} Dist '{dist_account}' on '{platform}' has {MAX_UPLOAD_DAILY - nbr_daily_upload - 1} upload(s) left")
                    cursor.execute(f"UPDATE dist_update SET daily_upload = {nbr_daily_upload + 1} WHERE dist = '{dist_account}' AND platform = '{platform}'")
                return True
            else:
                logger.info(f"{__name__} Dist '{dist_account}' on '{platform} has reached the daily upload limit: {MAX_UPLOAD_DAILY}")
                return False
        else:
            daily_upload = 1 if count else 0
            if count:
                cursor.execute(f"UPDATE dist_update SET daily_upload = {daily_upload}, limit_date_for_daily = '{datetime.now() + timedelta(days = 1, minutes = edge)}' WHERE dist = '{dist_account}' AND platform = '{platform}'")
            return True
        
        
@sql_connect('data/database.db')
def schedule_video(cursor_database : sqlite3.Cursor, dist_account : str, platform : str, id_table : str, edge : int = 10):
    last_scheduled = cursor_database.execute(f"SELECT id, schedule FROM data_content WHERE dist_account = '{dist_account}' AND dist_platform = '{platform}' AND schedule is not NULL ORDER BY schedule DESC LIMIT 1").fetchone()

    if last_scheduled is None:
        r_date = datetime.now() + timedelta(minutes = edge)
        cursor_database.execute(f"UPDATE data_content SET schedule = '{r_date}' WHERE id = '{id_table}'")
        logger.info(f"{__name__} : First video scheduled to {r_date} for dist '{dist_account}' on '{platform}'")
        return r_date
    else:
        last_scheduled_D = datetime.strptime(last_scheduled[1], '%Y-%m-%d %H:%M:%S.%f')
        th_date = last_scheduled_D + timedelta(days = 1, minutes = edge)
        if th_date < datetime.now():
            r_date = datetime.now() + timedelta(minutes = edge)
            cursor_database.execute(f"UPDATE data_content SET schedule = '{r_date}' WHERE id = '{id_table}'")
            logger.info(f"{__name__} : Video scheduled '{id_table}' to {r_date} for dist '{dist_account}' on '{platform}'")

            return r_date
        else : 
            cursor_database.execute(f"UPDATE data_content SET schedule = '{th_date}' WHERE id = '{id_table}'")
            logger.info(f"{__name__} : Video scheduled '{id_table}' to {th_date} for dist '{dist_account}' on '{platform}'")
            return th_date

@sql_connect("data/database.db")
def is_published(cursor_database : sqlite3.Cursor, id_table : int) : 
    cursor_database.execute(f"UPDATE data_content SET is_published = 1 WHERE id = '{id_table}'")

@sql_connect("data/database.db")
def is_processed(cursor_database : sqlite3.Cursor, id_table : int) : 
    cursor_database.execute(f"UPDATE data_content SET is_processed = 1 WHERE id = '{id_table}'")

@sql_connect("data/update_src.db")
def is_scrappable(cursor_upadte : sqlite3.Cursor, src_account : str, delta_days : int = 3):
    selection = cursor_upadte.execute("SELECT updated_time FROM src_update WHERE src = ?", (src_account,)).fetchone()
    return datetime.now() > datetime.strptime(selection[0], '%Y-%m-%d %H:%M:%S.%f') + timedelta(days = delta_days)

@sql_connect("data/database.db")
def remove_linked_content(cursor_database, id_video : int, filepath : str):
    selection = cursor_database.execute(f"SELECT filepath FROM data_content WHERE linked_to = '{id_video}'").fetchall()
    os.remove(filepath)
    for path in selection:
        os.remove(os.path.join(Path().cwd(), path[0]))

#Database Management of pools

@sql_connect('data/update_pools.db')
def create_table_update_pools(cursor : sqlite3.Cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS pool_update(
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        src TEXT NOT NULL,
        platform TEXT NOT NULL,
        updated_time TIMESTAMP NOT NULL,
        updated_counter INTEGER NOT NULL
    )"""
    )

@sql_connect('data/update_pools.db')
def update_one_pool(cursor : sqlite3.Cursor, src_account, platform):
    selection = cursor.execute(f"SELECT src, updated_counter FROM pool_update WHERE src = '{src_account}' AND platform = '{platform}' ").fetchone()
    if selection is None:
        cursor.execute(f"""INSERT INTO pool_update (src, platform, updated_time, updated_counter)
                       VALUES(?, ?, ?, ?)""", (src_account, platform, datetime.now(), 1))
    else :
        cursor.execute(f"UPDATE pool_update SET updated_counter = '{selection[1] + 1}', updated_time = '{datetime.now()}' WHERE src = '{src_account}' AND platform = '{platform}' ")
