import os
import json
import toml
import sys
import random
import logging

from tqdm import tqdm
from moviepy.video.fx.crop import crop
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.fx.margin import margin
from skimage.filters import gaussian

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import data_manager
from arc_manager import ArcManagement


constants = toml.load("core/create_content/constants.toml")

def return_all_dists_to_process_and_params() -> tuple[list[str], dict]:
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
    dist_params = {}
    for platform in all_dists.keys():
        file = f"arc/dist/{platform}.json"
        if os.path.exists(file):
            with open(file, "r") as f:
                dist = json.load(f)
            for account in all_dists[platform]:
                resp = dist.get(account, None)
                if resp is not None and resp.get("editing_options", None).get("edit", None) == True:
                    dist_to_process.append(account)
                    dist_params[account] = resp.get("editing_options", None)

    return dist_to_process, dist_params

@data_manager.sql_connect("data/database.db")
def load_pools_video(cursor):
    selection = cursor.execute("SELECT filepath FROM data_content WHERE role = 'pool'").fetchall()
    return [elem[0] for elem in selection]

def pick_a_color():
    l = [(255, 0, 127), (187, 11, 11), (102, 0, 153),
         (108, 2, 119), (0, 127, 255), (15, 5, 107),
         (102, 0, 255), (240, 195, 0), (223, 109, 20),
         (255, 255, 107), (128, 0, 128), (0, 142, 142)]
    return random.choice(l)

def blur_video(image):
    return gaussian(image.astype(float), sigma=0.7)

def process_content(filepath : str, params : dict = {}) -> bool:
    video = VideoFileClip(filename=filepath)
    width, height = video.w, video.h
    
    border = params.get("border", None)
    
    if border:
        if params.get("color", None) is not None:
            color = params["color"]
        else:
            color = pick_a_color()
    
    margin_size = params.get("margin_size", 9)
    
    if params.get("featuring_video", None) == True:
        pool_video = generate_pool_video(video.duration, width, (1-constants["SIZE_FACTOR"] + 0.3)*height, border = border, margin_size=margin_size, color=color)
        n_video = crop(video, width=width, height=height*constants["SIZE_FACTOR"], x_center=width/2, y_center=height/2)
    else : 
        n_video = video
    
    n_video = n_video.fl_image(blur_video)
    
    if border and params.get("featuring_video", None) == True:
        clips_array([[n_video], [pool_video]]).fx(margin, left=margin_size, right=margin_size, top=margin_size, bottom=margin_size, color=color).write_videofile(f"t/featured.mp4", fps=24, codec="libx264")
    elif params.get("featuring_video", None) == True:
        clips_array([[n_video], [pool_video]]).write_videofile(f"t/featured.mp4", fps=24, codec="libx264")
    elif border:
        n_video.fx(margin, left=margin_size, right=margin_size, top=margin_size, bottom=margin_size, color=color).write_videofile(f"t/featured.mp4", fps=24, codec="libx264")
    else:
        n_video.write_videofile(f"t/featured.mp4", fps=24, codec="libx264")

def generate_pool_video(time_to_fill : float, width : float, height : float, border : bool, margin_size = 7, color : tuple[int] = (0,0,0)) -> VideoFileClip:
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
    if border:
        return concatenate_videoclips(videos).set_audio(None).subclip(0, time_to_fill).fx(margin, top = margin_size, color=color) 
    else:
        return concatenate_videoclips(videos).set_audio(None).subclip(0, time_to_fill)


@data_manager.sql_connect("data/database.db")
def videos_processing_by_account(cursor_database, dist_account : str, params : dict):
    
    selection = cursor_database.execute(f"""
        SELECT id_filename, filepath, dist_account FROM data_content
        WHERE  is_processed = 0
        AND dist_account = '{dist_account}'
        AND role = 'content'
    """).fetchall()
    
    for content in tqdm(selection, desc=f"Processing videos for {dist_account}", unit="video"):
        process_content(filepath=content[1]) 
        
        logging.info(f"Video processing done for {content[1]} of {dist_account}")
        data_manager.is_processed(id_filename=content[0], params = params)
        
    logging.info(f"Videos processing done for {dist_account}")

def videos_processing(number_of_videos : int):
    
    all_dist_to_process, dist_params = return_all_dists_to_process_and_params()
    
    for dist_account, params in zip(all_dist_to_process, dist_params.keys()):
        videos_processing_by_account(dist_account=dist_account, params = dist_params[params])
    
    logging.info(f"Videos processing done for {all_dist_to_process}")
    
if __name__ == "__main__":
    print(return_all_dists_to_process_and_params())