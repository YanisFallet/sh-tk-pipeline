#load metadata for tiktok : max caption 2200 characters

import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import data_manager
import utils


@data_manager.sql_connect("data/database.db")
def load_metadata(cursor, dist_account : str, platform : str): 
    data = cursor.execute(f"""
        SELECT filepath, id_filename, description, dist_account, dist_platform, source_account, source_platform  FROM data_content
        WHERE  is_published = 0
        AND dist_account = '{dist_account}'
        AND dist_platform = '{platform}'
        AND role = 'content'
    """).fetchall()
    
    build_dict_type = lambda filepath, id_filename, description, dist_account, dist_platform, source_account, source_platform : {
            "filepath" : filepath,
            "id_filename" : id_filename,
            "caption" : build_description(description, dist_account ,dist_platform, source_account, source_platform),
            "dist_account" : dist_account
        }
    
    random.shuffle(data)
    
    data_l = [build_dict_type(*d) for d in data]
    
    return data_l

def build_description(description : str, dist_account : str, platform : str, source_account : str, source_platform : str)-> str:
    if utils.must_tagged(dist_account, platform):
        return f"Allez voir @{source_account} sur {source_platform} ! {description[0:2000]}"
    else : 
        return f"{description[0:2000]}"
    
    


if __name__ == "__main__": 
    print(load_metadata("ViesHorsDuCommun", "youtube"))