import os
import sys
import logging

from instaloader import Instaloader, Profile

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils
import data_manager
from arc_manager import ArcManagement

USER_WAITING_TIME = 2

logger = logging.getLogger(__name__)


class InstaScrapper:
    
    def __init__(self, channel_name : str, dist_platform : str, pool : str, role : str):
        self.channel_name = channel_name
        self.dist_platform = dist_platform
        self.pool = pool
        logger.info(f"InstaScrapper: {self.channel_name} - {self.dist_platform} - {self.pool}")
        
        if role in ["pool", "content"] : self.role = role
        else : raise ValueError("role must be 'pool' or 'content'")
        
        self.ARC = ArcManagement(src_p='instagram', dist_p=dist_platform)
        
        self.dw = Instaloader(
            dirname_pattern='content/reels',
            save_metadata=False,
            download_comments=False,
            post_metadata_txt_pattern="",
            filename_pattern="{shortcode}",
            download_video_thumbnails=False
        )
        
    def __load_past_videos(self):
        return data_manager.select_id_filename_by_src(self.channel_name, 'instagram')
    
    def __download_video(self):
        already_downloaded = self.__load_past_videos()
        profile = Profile.from_username(self.dw.context, self.channel_name)
        for post in profile.get_posts():
            if post.is_video:
                if not post.shortcode in already_downloaded:
                    self.dw.download_post(post, target=self.channel_name)
                    logger.info(f"Downloaded '{post.shortcode}'")
                    data_manager.insert_content_data(
                        source_account = self.channel_name,
                        source_platform = 'instagram',
                        dist_platform= self.dist_platform,
                        dist_account= utils.share_to_account(self.ARC.get_dist_by_pool(self.pool)),
                        pool = self.pool,
                        role = self.role,
                        filename = post.shortcode,
                        filepath = f"content/reels/{post.shortcode}.mp4",
                        **utils.extract_description_tags(post.caption)
                    )
                else:
                    break
        return True
        
    def __quit(self):
        self.dw.close()

    def run(self):
        self.__download_video()
        if self.role == "content" :data_manager.update_one_src(self.channel_name, 'instagram')
        elif self.role == "pool" : data_manager.update_one_pool(self.pool, 'instagram')
        self.__quit()
        
        
if __name__ == "__main__":
    insta = InstaScrapper('imangadzhi', 'youtube', "iman_gadzhi", role = "content")
    # insta.run()
    
    
    