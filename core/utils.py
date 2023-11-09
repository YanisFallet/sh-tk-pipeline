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

def share_to_account(dist_accounts : list) -> str:
    if len(dist_accounts) == 0:
        return None
    else :
        return random.choice(dist_accounts)

def remove_non_bmp_characters(input_string):
    result = ""
    for char in input_string:
        if ord(char) <= 0xFFFF:  # Vérifie si le point de code est dans le BMP
            result += char
    return result
    
def get_dist_data(dist_account: str, platform: str):
    file_path = f"arc/dist/{platform}.json"
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r") as f:
        data = json.load(f)
    return data.get(dist_account, None)

def must_tagged(dist_account: str, platform: str) -> bool:
    dist_data = get_dist_data(dist_account, platform)
    return bool(dist_data and dist_data.get("must_tagged", False))

def get_language(dist_account: str, platform: str) -> str:
    dist_data = get_dist_data(dist_account, platform)
    return dist_data.get("language", "fr") if dist_data else "fr"

@sql_connect('data/database.db')    
def update_share_to_account(cursor, src_p : str, dist_p : str):
    selection = cursor.execute("SELECT id, pool FROM data_content WHERE dist_account is NULL ").fetchall()
    ARC = ArcManagement(src_p=src_p, dist_p=dist_p)
    for elem in selection : 
        dist = ARC.get_dist_by_pool(elem[1])
        dist_account = share_to_account(dist)
        cursor.execute("UPDATE data_content SET dist_account = ? WHERE id = ?", (dist_account, elem[0]))


def split_text_m_h_t(text):
    i = 0
    result = []
    substr = ""
    while i < len(text):
        if text[i] == "#" or text[i] == "@":
            if substr:
                result.append(substr)
            substr = ""
            while i < len(text) and text[i] != " ":
                substr += text[i]
                i += 1
            result.append(substr)
            substr = ""
        else:
            substr += text[i]
        i += 1
    if substr:
        result.append(substr)
    return result