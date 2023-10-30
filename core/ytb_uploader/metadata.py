import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import data_manager
import utils


@data_manager.sql_connect("data/database.db")
def load_metadata(cursor, dist_account : str, platform : str): 
    data = cursor.execute(f"""
        SELECT id, filepath, id_filename, schedule, description, dist_account, source_account, source_platform, tags FROM data_content
        WHERE  is_published = 0
        AND is_processed = 1
        AND dist_account = '{dist_account}'
        AND dist_platform = '{platform}'
        AND role = 'content'
    """).fetchall()
    
    build_dict_type = lambda id_, filepath, id_filename, schedule, description, dist_account, source_account, source_platform, tags : {
            "id" : id_,
            "filepath" : filepath,
            "id_filename" : id_filename,
            "schedule" : schedule,
            "title" : title(description, dist_account, platform),
            "description" : build_description(description, dist_account, platform),
            "dist_account" : dist_account,
            "tags" : tags
        }
    
    random.shuffle(data)    
    
    data_l = [build_dict_type(*d) for d in data]
    
    return data_l

def get_title_prefix(dist_account: str, platform: str, source_account :str, source_platform :str) -> str:
    language = utils.get_language(dist_account, platform)
    return f"Check out @{source_account} on @{source_platform}" if language == "en" else f"Allez voir @{source_account} sur @{source_platform}"

def title(description: str, dist_account: str, platform: str, source_account :str, source_platform :str) -> str:
    if utils.must_tagged(dist_account, platform, source_account, source_platform):
        return get_title_prefix(dist_account, platform) + "... #shorts"
    else:
        return f"{description[:86].strip()}... #shorts"

def build_description(description: str, dist_account: str, platform: str,source_account : str, source_platform: str) -> str:
    if utils.must_tagged(dist_account, platform, source_account, source_platform):
        return get_title_prefix(dist_account, platform) + f"{description[:4000]}... #shorts"
    else:
        return f"{description[:4000].strip()}... #shorts"

if __name__ == "__main__": 
    print(load_metadata("imangadzhi", "tiktok"))