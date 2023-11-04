import os
import sys
import time
from functools import partial
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from abstract_scrapper import AbstractScrapper , get_driver
from arc_manager import ArcManagement
import data_manager
import utils
from logging_config import logger

USER_WAITING_TIME = 2

class TikTokScraper(AbstractScrapper):
    
    def __init__(self, driver, channel_name, dist_platform, pool,
                 to_the_bottom : bool = True,
                 optimized : bool = True,
                 role : str = "content"):
        
        self.optimized = optimized
        self.to_the_bottom = to_the_bottom
        self.driver = driver
        
        if role in ["pool", "content"] : self.role = role
        else : raise ValueError("role must be 'pool' or 'content'")
        
        self.ARC = ArcManagement(src_p='tiktok', dist_p=dist_platform)
        
        
        
        super().__init__(channel_name = channel_name,
                         content_name = 'tiktok',
                         dist_platform = dist_platform,
                         pool = pool)

    def __get_links(self):
        url = f"https://www.tiktok.com/{self.channel_name}"
        
        old_videos_id = data_manager.select_id_filename_by_src(self.channel_name, 'tiktok', self.dist_platform)
        
        self.driver.get(url)
        time.sleep(USER_WAITING_TIME)
        
        if self.to_the_bottom : self.scroll_page_to_the_end(self.driver)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        child_links = soup.find_all("a")
        #un peu cracra mais bon
        all_video_content = {}
        
        new_id = []
        for element in child_links:
            try:
                PRE_LINK = str(element.get("href"))
                n = PRE_LINK.split("/")[-1]
                if self.channel_name in PRE_LINK and "video" in PRE_LINK and not n in old_videos_id:
                    new_id.append(n)
                    comments = element.get('title')
                    all_video_content[n] = utils.extract_description_tags(comments)
            except:
                pass
        return new_id, all_video_content
        
    def __download_video(self, all_video_content, id_):
        path = os.path.join("content", "tiktok", f"{id_}.mp4")
        
        if not os.path.exists(path):
            url = f"https://www.tiktok.com/@{self.channel_name}/video/{id_}"
            session = requests.Session()
            server_url = 'https://musicaldown.com/'
            headers = {
                'authority': 'musicaldown.com',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'dnt': '1',
                'sec-ch-ua': '"Not?A_Brand";v="99", "Opera";v="97", "Chromium";v="111"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': self.get_headers()["User-Agent"]
            }
            session.headers.update(headers)
            request = session.get(server_url)
            data = {}
            parse = BeautifulSoup(request.text, 'html.parser')
            get_all_input = parse.findAll('input')
            for i in get_all_input:
                if i.get("id") == "link_url":
                    data[i.get("name")] = url
                else:
                    data[i.get("name")] = i.get("value")
            post_url = server_url + "id/download"
            req_post = session.post(post_url, data=data, allow_redirects=True)

            logger.info(f"{__name__} : Post response = {req_post.status_code} for {id_}")

            get_all_blank = BeautifulSoup(req_post.text, 'html.parser').findAll('a', attrs={'target': '_blank'})
            download_link = get_all_blank[0].get('href')
            get_content = requests.get(download_link, headers=self.get_headers(), allow_redirects=True)
            with open(os.path.join("content", "tiktok", f"{id_}.mp4"), 'wb') as f: f.write(get_content.content)
            
        dist_account = utils.share_to_account(self.ARC.get_dist_by_pool(self.pool))
            
        data_manager.insert_content_data('tiktok',
                                        self.channel_name, 
                                        self.dist_platform,
                                        dist_account, 
                                        self.pool, 
                                        self.role,
                                        f"content/tiktok/{id_}.mp4",
                                        id_, all_video_content[id_]["description"],
                                        all_video_content[id_]["tags"], 
                                        False
                                        )
        

    def __optimized_download_video(self, new_id, all_video_content):
        logger.info(f"{__name__} : Found {len(new_id)} new videos for {self.channel_name}")
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(partial(self.__download_video, all_video_content), new_id)
            
    def __non_optimized_download_video(self, new_id, all_video_content):
        logger.info(f"{__name__} : Found {len(new_id)} new videos for {self.channel_name}")
        for id_ in new_id:
            self.__download_video(all_video_content, id_)

    def run(self):
        new_id, all_video_content= self.__get_links()
        
        if self.optimized : self.__optimized_download_video(new_id, all_video_content)
        else : self.__non_optimized_download_video(new_id, all_video_content)
        
        if self.role == "content" : data_manager.update_one_src(self.channel_name, 'tiktok')
        elif self.role == "pool" : data_manager.update_one_pool(self.channel_name, 'tiktok')
        
        
        
if __name__ == '__main__':

    Tik = TikTokScraper(driver = get_driver("Profile 2", headless=False),
                        channel_name = "@incroyabledestin",
                        dist_platform = "youtube",
                        pool = "histoire_ia",
                        to_the_bottom = True,
                        optimized = True)
    Tik.run()
    