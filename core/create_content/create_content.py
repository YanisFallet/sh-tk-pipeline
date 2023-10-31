import os
import json
import toml
import sys
import random

from tqdm import tqdm
from moviepy.video.fx.crop import crop
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.fx.margin import margin
from skimage.filters import gaussian

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import data_manager
from arc_manager import ArcManagement
from logging_config import logger
logger.name = __name__

constants = toml.load("core/create_content/constants.toml")

def return_all_dists_to_process_and_params() -> tuple[dict, dict, dict]:
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

    dist_to_process = {}
    dist_to_not_process = {}
    dist_params = {}
    for platform in all_dists.keys():
        file = f"arc/dist/{platform}.json"
        if os.path.exists(file):
            with open(file, "r") as f:
                dist = json.load(f)
            for account in all_dists[platform]:
                resp = dist.get(account, None)
                if resp is not None and resp.get("editing_options", None).get("edit", None) == True:
                    dist_to_process[platform] = dist_to_process.get(platform, []) + [account]
                    dist_params[account] = resp.get("editing_options", None)
                else:
                    dist_to_not_process[platform] = dist_to_not_process.get(platform, []) + [account]

    return dist_to_not_process, dist_to_process, dist_params

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

def blur_video(image, sigma=0.2):
    return gaussian(image.astype(float), sigma=sigma)

def speedup_video(video : VideoFileClip, max_time : int = 59, overflow_time : int = 75):
    duration = video.duration
    if duration > max_time and duration < overflow_time:
        coeff = duration / max_time
        return video.speedx(coeff)
    elif duration > overflow_time:
        coeff = overflow_time / max_time
        v = video.subclip(0, overflow_time)
        return v.speedx(coeff)

def process_content(filepath : str, params : dict = {}) -> bool:
    video = VideoFileClip(filename=filepath)
    if video is None:
        logger.warning(f"Video {filepath} not found or video damaged")
        return False
    
    os.remove(filepath)
    width, height = video.w, video.h
    
    border = params.get("border", None)
    color = params.get("color", pick_a_color()) if border else None
    margin_size = params.get("margin_size", 9)
    featuring_video = params.get("featuring_video", False)
    
    if params.get("max_duration", None) is not None:
        video = speedup_video(video, max_time=params["max_duration"])
    
    if featuring_video:
        pool_video = generate_pool_video(video.duration, width, (1-constants["SIZE_FACTOR"] + 0.2)*height, border = border, margin_size=margin_size, color=color)
        n_video = crop(video, width=width, height=height*constants["SIZE_FACTOR"], x_center=width/2, y_center=height/2)
    else : 
        n_video = video
        
    n_video = n_video.fl_image(blur_video, params.get("coeff_blur", 0.2))
    
    if featuring_video:
        clips = clips_array([[n_video], [pool_video]])
        if border:
            clips = clips.fx(margin, left=margin_size, right=margin_size, top=margin_size, bottom=margin_size, color=color)
    elif border:
        clips = n_video.fx(margin, left=margin_size, right=margin_size, top=margin_size, bottom=margin_size, color=color)
    else:
        clips = n_video
    clips.write_videofile(filepath, fps=35, codec="libx264")
    
    return True

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
def videos_processing_by_account(cursor_database, dist_account : str, params : dict, to_process : bool = True):
    
    selection = cursor_database.execute(f"""
        SELECT id_filename, filepath, dist_account FROM data_content
        WHERE  is_processed = 0
        AND dist_account = '{dist_account}'
        AND role = 'content'
    """).fetchall()
    
    for content in tqdm(selection, desc=f"Processing videos for {dist_account}", unit="video"):
        processed = False
        
        if to_process:
            processed = process_content(filepath=content[1], params=params) 
        
        if processed :
            logger.info(f"Video processing done for {content[1]} of {dist_account}")
            data_manager.is_processed(id_filename=content[0])
        
    logger.info(f"Videos processing done for {dist_account}")

def videos_processing():
    
    dist_to_not_process, dist_to_process, dist_params = return_all_dists_to_process_and_params()
    
    platforms = ["tiktok", "youtube", "instagram"]
    
    for platform in platforms:
        n_dist_to_not_process = dist_to_not_process.get(platform, [])
        n_dist_to_process = dist_to_process.get(platform, [])
        
        for dist_account in n_dist_to_process:
            videos_processing_by_account(dist_account=dist_account, params = dist_params[dist_account], to_process = True)

        for dist_account in n_dist_to_not_process:
            videos_processing_by_account(dist_account=dist_account, params = {}, to_process=False)
    
    logger.info(f"Videos processing done for all accounts")
    
def videos_processing_by_dist_platform(dist_platform : str):
    dist_to_not_process, dist_to_process, dist_params = return_all_dists_to_process_and_params()
    
    n_dist_to_not_process = dist_to_not_process.get(dist_platform, [])
    n_dist_to_process = dist_to_process.get(dist_platform, [])
    
    for dist_account in n_dist_to_process:
        videos_processing_by_account(dist_account=dist_account, params = dist_params[dist_account], to_process = True)

    for dist_account in n_dist_to_not_process:
        videos_processing_by_account(dist_account=dist_account, params = {}, to_process=False)
    
    logger.info(f"Videos processing done for all accounts of {dist_platform}")
    

if __name__ == "__main__":
    print(return_all_dists_to_process_and_params())
    filepath = "t/7295812605162147104.mp4"
    p = {
            "edit" : True,
            "max_duration" : 59
        }
    process_content(filepath, p)