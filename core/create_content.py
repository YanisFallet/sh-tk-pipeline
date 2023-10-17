import os
import json
import random

from tqdm import tqdm
from moviepy.video.fx.crop import crop
from moviepy.video.fx import fadein, fadeout
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips

import data_manager
from arc_manager import ArcManagement

SIZE_FACTOR = 0.7


def return_all_dists_to_process():
    l = ["tiktok", "youtube", "instagram"]
    p_l = [(i, j) for i in l for j in l]
    
    all_dists = {}
    
    for elem in p_l:
        platform = elem[1]
        dist = ArcManagement(src_p=elem[0], dist_p=elem[1]).get_dist()
        
        if dist is not None and dist:
            if platform in all_dists:
                all_dists[platform].extend(dist)
            else:
                all_dists[platform] = dist
                
    dist_to_process = []
    for platform in all_dists.keys():
        file = f"arc/dist/{platform}.json"
        if os.path.exists(file):
            with open(file, "r") as f:
                dist = json.load(f)
            for account in all_dists[platform]:
                resp = dist.get(account, None)
                if resp is not None and resp.get("to_process", None) == True:
                    dist_to_process.append(account)

    return dist_to_process

@data_manager.sql_connect("data/database.db")
def load_pools_video(cursor):
    selection = cursor.execute("SELECT filepath FROM data_content WHERE role = 'pool'").fetchall()
    return [elem[0] for elem in selection]


@data_manager.sql_connect("data/database.db")
def videos_to_process_by_account(cursor_database, all_dists_to_process : str):
    
    selection = cursor_database.execute(f"""
        SELECT id_filename, filepath, dist_account FROM data_content
        WHERE  is_processed = 0
        AND role = 'content'
    """).fetchall()
    
    for content in tqdm(selection, desc="Processing videos", unit="video"):
        if content[2] in all_dists_to_process:
           process_content(*content) 
        
        
        data_manager.is_processed(id_filename=content[0])

def process_content(id_filename : str, filepath : str, dist_account : str):
    video = VideoFileClip(filename=filepath)
    width, height = video.w, video.h
    
    pool_video = generate_pool_video(video.duration, width, 0.3*height)
    
    clips_array([[video], [pool_video]]).write_videofile(f"featured.mp4", fps=24, codec="libx264")
    



def generate_pool_video(time_to_fill : float, width : float, height : float) -> VideoFileClip:
    filled = False
    pools_videos = load_pools_video()
    videos = []
    time_counter = 0
    while not filled:
        choice = random.choice(pools_videos)
        pools_videos.remove(choice)
        v = crop(VideoFileClip(choice), width=width, height=height, x_center=width/2, y_center=height/2)
        videos.append(v)
        time_counter += v.duration
        if time_counter >= time_to_fill:
            filled = True
    return concatenate_videoclips(videos).set_audio(None).subclip(0, time_to_fill)




if __name__ == "__main__":
    pass