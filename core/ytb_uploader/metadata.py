import os
import sys
import random

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import data_manager


@data_manager.sql_connect("data/database.db")
def load_metadata(cursor, dist_account : str, platform : str): 
    data = cursor.execute(f"""
        SELECT filepath, id_filename, schedule, description, dist_account, tags FROM data_content
        WHERE  is_published = 0
        AND dist_account = '{dist_account}'
        AND dist_platform = '{platform}'
        AND role = 'content'
    """).fetchall()
    
    build_dict_type = lambda filepath, id_filename, schedule, description, dist_account, tags : {
            "filepath" : filepath,
            "id_filename" : id_filename,
            "schedule" : schedule,
            "title" : title(description),
            "description" : description + " #shorts",
            "dist_account" : dist_account,
            "tags" : tags
        }
    
    random.shuffle(data)    
    
    data_l = [build_dict_type(*d) for d in data]
    
    return data_l

def title(description : str):
    if len(description) > 100:
        return description[:86].strip() + "... #shorts"
    else : return description

if __name__ == "__main__": 
    print(load_metadata("imangadzhi", "tiktok"))