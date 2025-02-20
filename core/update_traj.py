import os
import time

import utils
import data_manager
import arc_manager
from abstract_scrapper import get_driver

from tiktok_download import tk_download
from core.insta_download import insta_download

from ytb_uploader.ytb_uploader import YoutubeUploader
from tiktok_uploader.tiktok_uploader import TiktokUploader
from create_content.create_content import videos_processing, videos_processing_by_dist_platform

def create_all_tables():
    if not os.path.exists(os.path.join("data", "database.db")):
        data_manager.create_table_contents()
    
    if not os.path.exists(os.path.join("data", "update_src.db")):
        data_manager.create_table_update_src()
        
    if not os.path.exists(os.path.join("data", "update_dist.db")):
        data_manager.create_table_update_dist()

    if not os.path.exists(os.path.join("data", "update_pools.db")):
        data_manager.create_table_update_pools()
        

def update_traj_tiktok_to_ytb():
    #retrieve tiktok content
    ARC = arc_manager.ArcManagement(src_p='tiktok', dist_p='youtube')
    sources, pools = ARC.get_src(return_pools=True)
    driver = get_driver(profile = "Profile 3", headless=False)

    for source, pool in zip(sources, pools):
        to_the_bottom, is_useless = data_manager.update_src_is_bottom_useless(source, role = "content")
        if not is_useless:
            downloader = tk_download.TikTokScraper(
                driver = driver,
                channel_name = source,
                dist_platform = "youtube",
                pool= pool,
                to_the_bottom= to_the_bottom,
                optimized= True
            )
            downloader.run()
    
    driver.quit()
            
    utils.update_share_to_account(src_p="tiktok", dist_p="youtube")
    
    videos_processing_by_dist_platform(dist_platform="youtube")

    #cooldown
    time.sleep(5)
                
    google_accounts = ARC.get_google_accounts()
    
    for google_account in google_accounts:
        uploader = YoutubeUploader(
            google_account_name = google_account,
            source_platform = "tiktok"
        )
        
        uploader.run()
    
def update_traj_instagram_to_ytb():
    ARC = arc_manager.ArcManagement(src_p='instagram', dist_p='youtube')
    sources, pools = ARC.get_src(return_pools=True)
    
    for source, pool  in zip(sources, pools):
        to_the_bottom, is_useless = data_manager.update_src_is_bottom_useless(source, role = "content")
        if not is_useless:
            downloader = insta_download.InstaScrapper(
                channel_name = source,
                dist_platform = "youtube",
                pool = pool
            )
            downloader.run()
        
    utils.update_share_to_account(src_p="instagram", dist_p="youtube")
    
    videos_processing()
    
    time.sleep(5)
                
    google_accounts = ARC.get_google_accounts()
    
    for google_account in google_accounts:
        uploader = YoutubeUploader(
            google_account_name = google_account,
            source_platform = "tiktok"
        )
        
        uploader.run()
    
    
def update_traj_instagram_to_tiktok():
    ARC = arc_manager.ArcManagement(src_p='instagram', dist_p='tiktok')
    sources, pools = ARC.get_src(return_pools=True)
    
    print(f"sources : {sources}")
    
    # 1 - Download content from Instagram
    download_choice = input("Do you want to download from Instagram? (y/n): ")
    if download_choice.lower() == "y":
        for source, pool  in zip(sources, pools):
            to_the_bottom, is_useless = data_manager.update_src_is_bottom_useless(source, role = "content")
            print(f"is_useless {source} : {is_useless}")
            if not is_useless:
                downloader = insta_download.InstaScrapper(
                    channel_name = source,
                    dist_platform = "tiktok",
                    role = "content",
                    pool = pool,
                    optimized = True
                )
                downloader.run()
    
    utils.update_share_to_account(src_p="instagram", dist_p="tiktok")

    processing_choice = input("Do you want to process videos? (y/n): ")
    if processing_choice.lower() == "y":
        videos_processing_by_dist_platform(dist_platform="tiktok")
    
    upload_choice = input("Do you want to upload to TikTok? (y/n): ")
    if upload_choice.lower() == "y":
        google_accounts = ARC.get_google_accounts()

        for google_account in google_accounts:
            uploader = TiktokUploader(
                google_account_name = google_account,
                source_platform = "instagram"
            )
            uploader.run()
    
    
def update_traj_tiktok_to_tiktok():
    
    ARC = arc_manager.ArcManagement(src_p='tiktok', dist_p='tiktok')
    sources, pools = ARC.get_src(return_pools=True)
    driver = get_driver(profile = "Profile 5", headless=False)

    for source, pool in zip(sources, pools):
        to_the_bottom, is_useless = data_manager.update_src_is_bottom_useless(source, role = "content")
        if not is_useless:
            downloader = tk_download.TikTokScraper(
                driver = driver,
                channel_name = source,
                dist_platform = "tiktok",
                pool= pool,
                to_the_bottom= to_the_bottom,
                optimized= True
            )
            downloader.run()
    
    driver.quit()
    
    utils.update_share_to_account(src_p="tiktok", dist_p="tiktok")
    
    time.sleep(5)
    
    
    videos_processing_by_dist_platform(dist_platform="tiktok")
    
    google_accounts = ARC.get_google_accounts()
    
    for google_account in google_accounts:
        uploader = TiktokUploader(
            google_account_name = google_account,
            source_platform = "tiktok"
        )
        uploader.run()
    
    
if __name__ == "__main__":
    ARC = arc_manager.ArcManagement(src_p='instagram', dist_p='tiktok')
    sources, pools = ARC.get_src(return_pools=True)
    for source, pool in zip(sources, pools):
        print(source, pool)