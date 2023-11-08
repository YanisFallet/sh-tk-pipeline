import os
import json
import toml
import sys
import random
import concurrent.futures
from functools import partial


# // <button type="button" aria-label="@mention" class="jsx-4056857548 jsx-3119853737 jsx-3734900869 jsx-403562581 icon-style at"><svg fill="currentColor" font-size="18" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em"><path d="M24.28 44.54c-4.32 0-8.1-.87-11.33-2.6a18.05 18.05 0 0 1-7.49-7.2A21.94 21.94 0 0 1 2.87 23.9c0-4.04.87-7.57 2.6-10.61a18.21 18.21 0 0 1 7.43-7.15c3.2-1.7 6.88-2.55 11.04-2.55 4.04 0 7.59.77 10.66 2.3 3.1 1.51 5.5 3.67 7.2 6.49a18.19 18.19 0 0 1 2.6 9.79c0 3.52-.82 6.4-2.46 8.64-1.63 2.2-3.93 3.31-6.9 3.31-1.86 0-3.34-.4-4.42-1.2a4.6 4.6 0 0 1-1.73-3.7l.67.3a6.42 6.42 0 0 1-2.64 3.4 8.28 8.28 0 0 1-4.56 1.2 8.52 8.52 0 0 1-7.97-4.75 11.24 11.24 0 0 1-1.15-5.19c0-1.95.37-3.66 1.1-5.13a8.52 8.52 0 0 1 7.92-4.75c1.8 0 3.3.41 4.52 1.24 1.24.8 2.1 1.94 2.54 3.41l-.67.82v-4.04a1 1 0 0 1 1-1h2.27a1 1 0 0 1 1 1v12.05c0 .87.22 1.5.67 1.92.48.39 1.12.58 1.92.58 1.38 0 2.45-.75 3.22-2.26.8-1.53 1.2-3.44 1.2-5.7 0-3.05-.67-5.69-2.02-7.93a12.98 12.98 0 0 0-5.52-5.13 17.94 17.94 0 0 0-8.3-1.83c-3.3 0-6.23.69-8.79 2.07a14.82 14.82 0 0 0-5.9 5.76 17.02 17.02 0 0 0-2.11 8.59c0 3.39.7 6.35 2.11 8.88 1.4 2.5 3.4 4.41 6 5.76a19.66 19.66 0 0 0 9.17 2.01h10.09a1 1 0 0 1 1 1v2.04a1 1 0 0 1-1 1H24.28Zm-1-14.12c1.72 0 3.08-.56 4.07-1.68 1.03-1.12 1.54-2.64 1.54-4.56 0-1.92-.51-3.44-1.54-4.56a5.17 5.17 0 0 0-4.08-1.68c-1.7 0-3.05.56-4.08 1.68-.99 1.12-1.49 2.64-1.49 4.56 0 1.92.5 3.44 1.5 4.56a5.26 5.26 0 0 0 4.07 1.68Z"></path></svg></button>

# // <button type="button" aria-label="Hashtag" class="jsx-4056857548 jsx-3119853737 jsx-3734900869 jsx-403562581 icon-style hash"><svg fill="currentColor" font-size="20" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em"><path fill-rule="evenodd" clip-rule="evenodd" d="m17.74 15.5.68-6.6a1 1 0 0 1 1-.9h.97a1 1 0 0 1 1 1.1l-.63 6.4h7.98l.68-6.6a1 1 0 0 1 1-.9h.97a1 1 0 0 1 1 1.1l-.63 6.4H37a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1h-5.54l-.8 8H36a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1h-5.64l-.78 7.6a1 1 0 0 1-1 .9h-.97a1 1 0 0 1-1-1.1l.73-7.4h-7.98l-.78 7.6a1 1 0 0 1-1 .9h-.97a1 1 0 0 1-1-1.1l.73-7.4H11a1 1 0 0 1-1-1v-1a1 1 0 0 1 1-1h5.64l.8-8H12a1 1 0 0 1-1-1v-1a1 1 0 0 1 1-1h5.74Zm2.72 3-.8 8h7.98l.8-8h-7.98Z"></path></svg></button>


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

    final_clip.write_videofile(filepath, fps=25, codec = "libx264", threads = 10, preset = "ultrafast", logger=None)

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
    
    print(selection)
    
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

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(constants["NBR_PROCESSING_DAY_ACCOUNT"]//2, 10)) as executor:
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