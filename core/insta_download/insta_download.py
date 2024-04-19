import os
import sys
import time
import requests


from concurrent.futures import ThreadPoolExecutor

from instaloader import Instaloader, Profile


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils
import data_manager
from arc_manager import ArcManagement
from logging_config import logger
from abstract_scrapper import AbstractScrapper
logger.name = __name__

USER_WAITING_TIME = 2
MAX_REELS_TO_LOOK = 25

class InstaScrapper:
    
    def __init__(self, channel_name : str, dist_platform : str, pool : str, role : str, optimized : bool = False):
        self.channel_name = channel_name
        self.dist_platform = dist_platform
        self.pool = pool
        self.optimized = optimized
        
        if role in ["pool", "content"] : self.role = role
        else : raise ValueError("role must be 'pool' or 'content'")
        
        os.makedirs("content/reels", exist_ok=True)
        
        self.Abc = AbstractScrapper(channel_name, 'reels', dist_platform, pool)
        
        self.ARC = ArcManagement(src_p='instagram', dist_p=dist_platform)
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
                        self.get_video_rapidapi(f"content/reels/{target_file}.mp4", post.shortcode)
                        logger.info(f"{__name__} : Downloaded '{post.shortcode}'")
                    else :
                        i = 1
                        while os.path.exists(f"content/reels/{post.shortcode}_{i}.mp4"):
                            i += 1
                        target_file = f"{post.shortcode}_{i}"
                        self.get_video_rapidapi(f"content/reels/{target_file}.mp4", post.shortcode)
                        logger.info(f"{__name__} : Downloaded '{post.shortcode}_{i}'")
                    
                    if os.path.exists(f"content/reels/{target_file}.mp4"):    
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
                        logger.info(f"{__name__} : Failed to download '{post.shortcode} probleme insta'")
                else:
                    break
            time.sleep(1/2)
        return True
    
    def __download_video_opti(self):
        already_downloaded = self.load_past_videos()
        profile = Profile.from_username(self.dw.context, self.channel_name)
        posts = profile.get_posts()
        posts = list(set(profile.get_posts()))[:MAX_REELS_TO_LOOK]

        with ThreadPoolExecutor(max_workers=2) as executor:
            executor.map(self.__process_post, posts, [already_downloaded]*len(posts))

    def __process_post(self, post, already_downloaded):
        if post.is_video and post.shortcode not in already_downloaded:
            print(post.shortcode)
            if not os.path.exists(f"content/reels/{post.shortcode}.mp4"):
                target_file = post.shortcode
                self.get_video_rapidapi(f"content/reels/{target_file}.mp4", post.shortcode)
                logger.info(f"{__name__} : Downloaded '{post.shortcode}'")
            else :
                i = 1
                while os.path.exists(f"content/reels/{post.shortcode}_{i}.mp4"):
                    i += 1
                target_file = f"{post.shortcode}_{i}"
                self.get_video_rapidapi(f"content/reels/{target_file}.mp4", post.shortcode)
                logger.info(f"{__name__} : Downloaded '{post.shortcode}_{i}'")

            if os.path.exists(f"content/reels/{target_file}.mp4"):
                print(f"{post.shortcode} downloaded")
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
                logger.info(f"{__name__} : Failed to download '{post.shortcode} probleme insta'")
    
    def get_video_save_free(self, target_file : str, postcode : str):
        session = requests.Session()
        server_url = "https://www.save-free.com/process"
        reel = f"https://www.instagram.com/reel/{postcode}/" 
        headers = {
            'authority': 'www.save-free.com',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-functional=no; cookielawinfo-checkbox-performance=no; cookielawinfo-checkbox-analytics=no; cookielawinfo-checkbox-others=no; _ga=GA1.1.1742836606.1711754176; HstCfa4752989=1711754175805; HstCmu4752989=1711754175805; HstPn4752989=1; c_ref_4752989=https%3A%2F%2Fwww.google.com%2F; _gcl_au=1.1.1171069348.1711754176; HstCla4752989=1712933311640; HstPt4752989=3; HstCnv4752989=3; HstCns4752989=3; cf_clearance=okCVzk3JvoWvf5EWDLeku4jVvIUGQKyLfzwSLZc3pkI-1712933311-1.0.1.1-zntjVp7EOzbeskar7M2n8KdQdjXCjbmnua8QoD26Ya7f9cdp4at0eCxxOik08hN6XBG5b.cQ_UFDy6mfGp60NQ; _ga_9M9G1NYVWE=GS1.1.1712933311.3.0.1712933329.42.0.0; _ga_TCKL78VSRE=GS1.1.1712933311.3.0.1712933329.42.0.0',
            'Origin': 'https://www.save-free.com',
            'Referer': 'https://www.save-free.com/fr/reels-downloader/',
            'Sec-Ch-Ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"macOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.Abc.get_headers()["User-Agent"],
            'X-Requested-With': 'XMLHttpRequest',
            'X-Valy-Cache': 'accpted'
        }
        
        data = {
            "instagram_url" : reel,
            "type" : 'media',
            "resource" : "save"
        }
        session.headers.update(headers)
        iteration = 0
        while iteration < 10:
            post_res = session.post(server_url, data=data, allow_redirects=True)
            print(f"Post response = {post_res.status_code} for {postcode}")
            if post_res.status_code == 200:
                break
            time.sleep(2)
            iteration += 1

        video = session.get(post_res.json()[0]['url'][0]['url'])
        with open(target_file, "wb") as f:
            f.write(video.content)

        video = session.get(post_res.json()[0]['url'][0]['url'])
        
        with open(target_file, "wb") as f:
            f.write(video.content)
            
            
    def get_video_rapidapi(self, target_file: str, postcode: str):
        url = "https://instagram-post-and-reels-downloader.p.rapidapi.com/"

        querystring = {"url":f"https://www.instagram.com/reel/{postcode}/?utm_source=ig_web_copy_link&igshid=MzRlODBiNWFlZA=="}

        headers = {
	        "X-RapidAPI-Key": "54496de620msh757cc1a67c03c7ap1e8223jsnb511d6ace562",
	        "X-RapidAPI-Host": "instagram-post-and-reels-downloader.p.rapidapi.com"
        }
        i = 30
        while i > 0:
            response = requests.get(url, headers=headers, params=querystring)
            if len(response.json()) > 0:
                break
            time.sleep(1)
            i -= 1
            if i == 0:
                logger.info(f"{__name__} : Failed to download '{postcode} probleme rapidapi'")
                return False
            
        video = requests.get(response.json()[0]["link"])
        with open(target_file, "wb") as f:
            f.write(video.content)

    def __quit(self):
        self.dw.close()

    def run(self):
        if self.optimized : self.__download_video_opti()
        else : self.__download_video()
        
        if self.role == "content" :data_manager.update_one_src(self.channel_name, 'instagram')
        elif self.role == "pool" : data_manager.update_one_pool(self.pool, 'instagram')
        self.__quit()
        

        
        
if __name__ == "__main__":
    downloader = InstaScrapper(
        channel_name = "reelsofnorway",
        dist_platform = None,
        role="content",
        pool = "short",
        optimized = False
    )
    downloader.get_video_rapidapi("content/reels/test.mp4", "C3Ka7z3q0tr")
    
    
    
    