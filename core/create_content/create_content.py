import os
import json
import toml
import sys
import random
import concurrent.futures
from functools import partial

from tqdm import tqdm
from moviepy.video.fx.crop import crop
from moviepy.editor import VideoFileClip, clips_array, concatenate_videoclips
from moviepy.video.fx.margin import margin
from skimage.filters import gaussian

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import data_manager
from arc_manager import ArcManagement
from logging_config import logger

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
def load_pools_video(cursor, pool_name : str = None):
    if pool_name is None:
        selection = cursor.execute("SELECT filepath FROM data_content WHERE role = 'pool'").fetchall()
    else:
        selection = cursor.execute("SELECT filepath FROM data_content WHERE role = 'pool' AND pool = ?", (pool_name,)).fetchall()
        if len(selection) == 0:
            logger.warning(f"{__name__} : No pool video found for {pool_name}")
            selection = cursor.execute("SELECT filepath FROM data_content WHERE role = 'pool'").fetchall()
    return [elem[0] for elem in selection]

@data_manager.sql_connect("data/database.db")
def check_video(cursor_database, path : str, min_duration : int = 2, dimensions_allowed : list[tuple, tuple] = [(0, 0), (4000, 4000)]):
    abs_path = os.path.join(os.getcwd(), path)
    
    if not os.path.exists(abs_path):
        cursor_database.execute("""
            UPDATE data_content
            SET is_processed = 1,
            is_corrupted = 1,
            is_published = 1
            WHERE filepath = ?
        """, (path,))
        return False
    try: 
        clip = VideoFileClip(path)
        
    except OSError:
        cursor_database.execute("""
            UPDATE data_content
            SET is_processed = 1,
            is_corrupted = 1,
            is_published = 1
            WHERE filepath = ?
        """, (path,))
        os.remove(abs_path)
        return False
    
    to_wipe_out = False
    # Check duration
    if clip.duration < min_duration:
        logger.warning(f"{__name__} : Video too short for {path}")
        to_wipe_out = True
    
    # Check dimensions
    if not (clip.size[0] in range(dimensions_allowed[0][0], dimensions_allowed[1][0]) and clip.size[1] in range(dimensions_allowed[0][1], dimensions_allowed[1][1])):
        logger.warning(f"{__name__} : Video dimensions not allowed for {path}")
        to_wipe_out = True
        
    if to_wipe_out:
        cursor_database.execute("""
            UPDATE data_content
            SET is_processed = 1,
            is_corrupted = 1,
            is_published = 1
            WHERE filepath = ?
        """, (path,))
        os.remove(abs_path)
        return False
    
    return True
        
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
    
    
def build_longer_videos(id_table : int, video : VideoFileClip, min_time: int, gap_time : int = 5):
    duration = video.duration
    if duration + gap_time >= min_time:
        coeff = duration / min_time + 0.001
        return video.speedx(coeff)
    else:
        video = compile_videos(id_table, video, min_time)
        return video
    
@data_manager.sql_connect("data/database.db")
def compile_videos(cursor_database, id_table : int, video : VideoFileClip, min_time : int):
    video_selection = cursor_database.execute("""
        SELECT id, filepath FROM data_content
        WHERE (dist_account, platform) = (
            SELECT dist_account, platform FROM data_content
            WHERE id = ?
        )
        AND role = 'content'
        AND is_published = 0
        AND is_processed = 0
    """, (id_table,)).fetchall()

    videos = [video]
    id_list = []
    time_counter = video.duration

    while time_counter < min_time and video_selection:
        choice = random.choice(video_selection)
        video_selection.remove(choice)

        v = VideoFileClip(choice[1])
        videos.append(v)
        id_list.append(choice[0])

        time_counter += v.duration

    cursor_database.executemany("""
        UPDATE data_content
        SET is_processed = 1,
        is_published = 1,
        linked_to = ?
        WHERE id = ?
    """, ((id_table, id_) for id_ in id_list))

    return concatenate_videoclips(videos)

@data_manager.sql_connect("data/database.db")
def process_content(cursor, id_table : int, filepath : str, params : dict = {}) -> bool:
    
    if not check_video(filepath):
        logger.info(f"{__name__} : Video {filepath} not found or video damaged")
        return False

    is_processed = cursor.execute("SELECT is_processed FROM data_content WHERE id = ?", (id_table,)).fetchone()[0]
    if is_processed:
        logger.info(f"{__name__} : Video {filepath} already processed")
        return False

    video_clip = VideoFileClip(filename=filepath)
    os.remove(filepath)

    border = params.get("border", None)
    color = params.get("color", pick_a_color()) if border else None
    margin_size = params.get("margin_size", 9)
    is_featuring_video = params.get("featuring_video", False)
    max_duration = params.get("max_duration", None)
    min_duration = params.get("min_duration", None)

    if min_duration and max_duration and min_duration > max_duration:
        logger.error(f"min_duration > max_duration for {filepath}")
        raise ValueError(f"min_duration > max_duration for {filepath}")

    if max_duration:
        video_clip = speedup_video(video_clip, max_time=max_duration)

    if min_duration:
        video_clip = build_longer_videos(id_table, video_clip, min_time=min_duration)

    if is_featuring_video:
        pool_video = generate_pool_video(video_clip.duration, video_clip.w, (1-constants["SIZE_FACTOR"] + 0.2)*video_clip.h, pool_name=params.get("f_video_pool_name", None), border=border, margin_size=margin_size, color=color)
        video_clip = crop(video_clip, width=video_clip.w, height=video_clip.h*constants["SIZE_FACTOR"], x_center=video_clip.w/2, y_center=video_clip.h/2)

    video_clip = video_clip.fl_image(partial(blur_video, sigma=params.get("coeff_blur", 0.2)))

    if is_featuring_video:
        final_clip = clips_array([[video_clip], [pool_video]])
    else:
        final_clip = video_clip

    if border:
        final_clip = final_clip.fx(margin, left=margin_size, right=margin_size, top=margin_size, bottom=margin_size, color=color)

    # final_clip.write_videofile(filepath, fps=25, codec = "libx264", threads = 10, preset = "ultrafast", logger=None)
    final_clip.write_videofile(filepath, fps=25, codec = "libx264", threads = 3, logger=None)

    return True

def generate_pool_video(time_to_fill : float, width : float, height : float, pool_name : str = None, border : bool = False, margin_size = 7, color : tuple[int] = (0,0,0)) -> VideoFileClip:
    filled = False
    pools_videos = load_pools_video(pool_name=pool_name)
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
        SELECT id, filepath, dist_account FROM data_content
        WHERE  is_processed = 0
        AND dist_account = '{dist_account}'
        AND role = 'content'
        LIMIT {constants["NBR_PROCESSING_DAY_ACCOUNT"]}
    """).fetchall()
    
    for content in tqdm(selection, desc=f"Processing videos for {dist_account}", unit="video"):
        processed = False
        
        if to_process:
            processed = process_content(id_table = content[0], filepath=content[1], params=params) 
        
        if processed :
            logger.info(f"{__name__} : Video processing done for {content[1]} of {dist_account}")
            data_manager.is_processed(id_table=content[0])
        else : 
            logger.info(f"{__name__} : Video processing failed for {content[1]} of {dist_account} or already done")
    logger.info(f"{__name__} : Videos processing done for {dist_account}")
    
@data_manager.sql_connect("data/database.db")
def videos_processing_by_account_concurrent(cursor_database, dist_account: str, params: dict, to_process: bool = True):
    selection = cursor_database.execute(f"""
        SELECT id, filepath, dist_account FROM data_content
        WHERE  is_processed = 0
        AND dist_account = '{dist_account}'
        AND role = 'content'
        LIMIT {constants["NBR_PROCESSING_DAY_ACCOUNT"]}
    """).fetchall()
    
    def process_video(content):
        id_table, filepath, _ = content
        processed = False

        if to_process:
            processed = process_content(id_table=id_table, filepath=filepath, params=params)

        if processed:
            logger.info(f"{__name__} : Video processing done for {filepath} of {dist_account}")
            data_manager.is_processed(id_table=id_table)
        else:
            logger.info(f"{__name__} : Video processing failed for {filepath} of {dist_account} or already done")

    with concurrent.futures.ThreadPoolExecutor(max_workers= 10) as executor:
        list(executor.map(process_video, selection))

    logger.info(f"{__name__} : Videos processing done for {dist_account}")

def videos_processing():
    dist_to_not_process, dist_to_process, dist_params = return_all_dists_to_process_and_params()
    
    platforms = ["tiktok", "youtube", "instagram"]
    
    for platform in platforms:
        n_dist_to_not_process = dist_to_not_process.get(platform, [])
        n_dist_to_process = dist_to_process.get(platform, [])
        
        for dist_account in n_dist_to_process:
            videos_processing_by_account_concurrent(dist_account=dist_account, params = dist_params[dist_account], to_process = True)

        for dist_account in n_dist_to_not_process:
            videos_processing_by_account(dist_account=dist_account, params = {}, to_process=False)

    logger.info(f"{__name__} : Videos processing done for all accounts")
    
def videos_processing_by_dist_platform(dist_platform : str):
    dist_to_not_process, dist_to_process, dist_params = return_all_dists_to_process_and_params()
    
    n_dist_to_not_process = dist_to_not_process.get(dist_platform, [])
    n_dist_to_process = dist_to_process.get(dist_platform, [])
    
    for dist_account in n_dist_to_process:
        videos_processing_by_account_concurrent(dist_account=dist_account, params = dist_params[dist_account], to_process = True)

    for dist_account in n_dist_to_not_process:
        videos_processing_by_account(dist_account=dist_account, params = {}, to_process=False)
    
    logger.info(f"{__name__} : Videos processing done for all accounts of {dist_platform}")
    

if __name__ == "__main__":
    videos_processing_by_dist_platform("tiktok")