import os
import sys
import requests
from concurrent.futures import ThreadPoolExecutor

from instaloader import Instaloader, Profile

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils
import data_manager
from arc_manager import ArcManagement
from logging_config import logger
logger.name = __name__

USER_WAITING_TIME = 2
MAX_REELS_TO_LOOK = 100


class InstaScrapper:
    
    def __init__(self, channel_name : str, dist_platform : str, pool : str, role : str, opti : bool = False):
        self.channel_name = channel_name
        self.dist_platform = dist_platform
        self.pool = pool
        self.opti = opti
        
        if role in ["pool", "content"] : self.role = role
        else : raise ValueError("role must be 'pool' or 'content'")
        
        self.ARC = ArcManagement(src_p='instagram', dist_p=dist_platform)
        
        
        self.headers = {
            "X-RapidAPI-Key": "54496de620msh757cc1a67c03c7ap1e8223jsnb511d6ace562",
            "X-RapidAPI-Host": "instagram-post-and-reels-downloader.p.rapidapi.com"
        }
        
        self.dw = Instaloader(
            dirname_pattern='content/reels',
            save_metadata=False,
            download_comments=False,
            post_metadata_txt_pattern="",
            filename_pattern="{shortcode}",
            download_video_thumbnails=False
        )
        
    def load_past_videos(self):
        return data_manager.select_id_filename_by_src(self.channel_name, 'instagram', self.dist_platform, self.role)
    
    def __download_video(self):
        already_downloaded = self.load_past_videos()
        profile = Profile.from_username(self.dw.context, self.channel_name)
        for post in list(set(profile.get_posts()))[:MAX_REELS_TO_LOOK]:
            if post.is_video:
                if not post.shortcode in already_downloaded:
                    if not os.path.exists(f"content/reels/{post.shortcode}.mp4"):
                        target_file = post.shortcode
                        self._get_video(f"content/reels/{target_file}.mp4", post.shortcode)
                        logger.info(f"{__name__} : Downloaded '{post.shortcode}'")
                    else :
                        i = 1
                        while os.path.exists(f"content/reels/{post.shortcode}_{i}.mp4"):
                            i += 1
                        target_file = f"{post.shortcode}_{i}"
                        self._get_video(f"content/reels/{target_file}.mp4", post.shortcode)
                        logger.info(f"{__name__} : Downloaded '{post.shortcode}_{i}'")
                        
                    data_manager.insert_content_data(
                        source_account = self.channel_name,
                        source_platform = 'instagram',
                        dist_platform= self.dist_platform,
                        dist_account= utils.share_to_account(self.ARC.get_dist_by_pool(self.pool)) if self.role == "content" else None,
                        pool = self.pool,
                        role = self.role,
                        filename = target_file,
                        filepath = f"content/reels/{target_file}.mp4",
                        **utils.extract_description_tags(post.caption)
                    )
                else:
                    break
        return True
    
    def __download_video_opti(self):
        already_downloaded = self.load_past_videos()
        profile = Profile.from_username(self.dw.context, self.channel_name)
        posts = list(set(profile.get_posts()))[:MAX_REELS_TO_LOOK]

        with ThreadPoolExecutor() as executor:
            executor.map(self.__process_post, posts, [already_downloaded]*len(posts))

    def __process_post(self, post, already_downloaded):
        if post.is_video and post.shortcode not in already_downloaded:
            if not os.path.exists(f"content/reels/{post.shortcode}.mp4"):
                target_file = post.shortcode
                self._get_video(f"content/reels/{target_file}.mp4", post.shortcode)
                logger.info(f"{__name__} : Downloaded '{post.shortcode}'")
            else :
                i = 1
                while os.path.exists(f"content/reels/{post.shortcode}_{i}.mp4"):
                    i += 1
                target_file = f"{post.shortcode}_{i}"
                self._get_video(f"content/reels/{target_file}.mp4", post.shortcode)
                logger.info(f"{__name__} : Downloaded '{post.shortcode}_{i}'")

            data_manager.insert_content_data(
                source_account = self.channel_name,
                source_platform = 'instagram',
                dist_platform= self.dist_platform,
                dist_account= utils.share_to_account(self.ARC.get_dist_by_pool(self.pool)) if self.role == "content" else None,
                pool = self.pool,
                role = self.role,
                filename = target_file,
                filepath = f"content/reels/{target_file}.mp4",
                **utils.extract_description_tags(post.caption)
            )
    
    def _get_video(self, target_file : str, postcode : str):
        url = "https://instagram-post-and-reels-downloader.p.rapidapi.com/"
        querystring = {"url":f"https://www.instagram.com/reel/{postcode}/?utm_source=ig_web_copy_link&igshid=MzRlODBiNWFlZA=="}
        headers = {
            "X-RapidAPI-Key": "54496de620msh757cc1a67c03c7ap1e8223jsnb511d6ace562",
            "X-RapidAPI-Host": "instagram-post-and-reels-downloader.p.rapidapi.com"
        }
        
        response = requests.get(url, headers=headers, params=querystring)
        content= requests.get(response.json()[0]["link"])

        with open(target_file, "wb") as f:
            f.write(content.content)

    def __quit(self):
        self.dw.close()

    def run(self):
        if self.opti : self.__download_video_opti()
        else : self.__download_video()
        
        if self.role == "content" :data_manager.update_one_src(self.channel_name, 'instagram')
        elif self.role == "pool" : data_manager.update_one_pool(self.pool, 'instagram')
        self.__quit()
        
        
if __name__ == "__main__":
    insta = InstaScrapper('imangadzhi', 'youtube', "iman_gadzhi", role = "content")
    
    
    
    