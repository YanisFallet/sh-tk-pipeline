import os
import time

import data_manager
from abstract_scrapper import get_driver
from arc_manager import ArcManagement
from insta_download.insta_download import InstaScrapper
from tiktok_download.tk_download import TikTokScraper

class UpdatePools:
    
    def __init__(self):
        pass
        
    def __download_pool_instagram(self):
        arc = ArcManagement(src_p='instagram', dist_p=None)
        pools_accounts, pools_theme = arc.get_pools_by_platform()
        print(pools_accounts, pools_theme)
        for pool_account, pool_theme in zip(pools_accounts, pools_theme):
            to_the_bottom, is_useless = data_manager.update_src_is_bottom_useless(pool_account, role = "pool")
            if not is_useless:
                downloader = InstaScrapper(
                    channel_name = pool_account,
                    dist_platform = None,
                    role="pool",
                    pool = pool_theme
                )
                downloader.run()
            
    def __download_pool_tiktok(self):
        arc = ArcManagement(src_p='tiktok', dist_p=None)
        pools_accounts, pools_theme = arc.get_pools_by_platform()
        for pool_account, pool_theme in zip(pools_accounts, pools_theme):
            to_the_bottom, is_useless = data_manager.update_src_is_bottom_useless(pool_account, role = "pool")
            if not is_useless:
                downloader = TikTokScraper(
                    channel_name = pool_account,
                    driver=get_driver(profile="Profile 2", headless=False),
                    dist_platform = None,
                    pool = pool_theme,
                    role="pool",
                    to_the_bottom = to_the_bottom,
                    optimized = True
                )
                downloader.run()

    def run(self):
        self.__download_pool_instagram()
        time.sleep(2)
        self.__download_pool_tiktok()
        
        
if __name__ == "__main__":
    print(ArcManagement.get_pools_by_platform("instagram"))
            
        
        
        