import os
import json
import random

from moviepy.editor import VideoFileClip

from data_manager import sql_connect
from arc_manager import ArcManagement


def extract_description_tags(caption_text : str):
    return {"description" : remove_non_bmp_characters(caption_text), 
            "tags" : ",".join([remove_non_bmp_characters(tag.strip("#")) for tag in caption_text.split() if tag.startswith('#')])}

def get_id_by_channel(channel_name :str) -> str:
    with open("arc/ytb_channels_id.json", "r") as f:
        return json.load(f)[channel_name]

def extract_id_from_url_insta(url : str) -> str:
    return url.split("/")[-1].split("?")[0]

def reformat_json_files(directory_path):
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    data = json.load(f)
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=10, sort_keys=True)
                    
def share_to_account(list_accounts : list[str]):
    if len(list_accounts) == 0:
        return ""
    else:
        return random.choice(list_accounts)

def remove_non_bmp_characters(input_string):
    result = ""
    for char in input_string:
        if ord(char) <= 0xFFFF:  # Vérifie si le point de code est dans le BMP
            result += char
    return result

def cut_videos(path : str, max_time : int = 60):
    clip = VideoFileClip(path)
    duration = clip.duration
    if duration > max_time:
        clip.set_duration(max_time)
        clip.write_videofile(path, fps=24, codec="libx264", threads=4, preset="ultrafast")

@sql_connect('data/database.db')    
def update_share_to_account(cursor, src_p : str, dist_p : str):
    selection = cursor.execute("SELECT id, pool FROM data_content WHERE dist_account is NULL ").fetchall()
    ARC = ArcManagement(src_p=src_p, dist_p=dist_p)
    for elem in selection : 
        dist = ARC.get_dist_by_pool(elem[1])
        dist_account = share_to_account(dist)
        cursor.execute("UPDATE data_content SET dist_account = ? WHERE id = ?", (dist_account, elem[0]))



 
    