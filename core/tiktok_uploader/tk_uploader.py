import os
import sys
import time
import json
import toml
from pathlib import Path


from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tiktok_uploader.metadata import load_metadata

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils
import data_manager
from abstract_scrapper import get_driver
from arc_manager import ArcManagement

from logging_config import logger

constants = toml.load("core/tiktok_uploader/constants.toml")

class TiktokUploader:
    
    def __init__(self, 
                google_account_name : str,
                source_platform : str):
    
        if not google_account_name in ["shortsfactory33", "yanis.fallet", "picorp696"]:
            raise Exception(f"Google account '{google_account_name}' name not found")

        self.ARC = ArcManagement(src_p=source_platform, dist_p="tiktok")
            
        self.google_account_name = google_account_name
        self.source_platform = source_platform
        self.dist_account : list = self.ARC.get_dist_by_google_account(self.google_account_name)
        
        if len(self.dist_account) != 1:
            raise Exception(f"Google account '{google_account_name}' is not linked to one and only one Tiktok account : {len(self.all_dist_accounts)} found")

    def __get_driver_t(self):
        self.browser = get_driver(self.__get_profile_path(self.google_account_name), headless = False)
        
    def __get_profile_path(self, google_account_name : str) -> dict:
        with open('arc/utils/google_dir.json') as f:
            return json.load(f)[google_account_name]
        
    def __get_to_tiktok_upload(self):
        self.browser.get(constants["TIKTOK_CREATOR_CENTER"])
        time.sleep(constants["USER_WAITING_TIME"])
        
    def __inject_caption(self, text : str):
        "Inject caption in the caption input"
        split_text : list[str] = utils.split_text_m_h_t(text)
        caption = self.browser.find_element(By.XPATH, constants["CAPTION_INPUT"])
        time.sleep(constants["USER_WAITING_TIME"])
        caption.clear()
        for elem_t in split_text:
            if elem_t.startswith("#"):
                self.browser.find_element(By.XPATH, constants["HASHTAG_BUTTON"]).click()
                caption.send_keys(elem_t.strip("#"))
                time.sleep(constants["USER_WAITING_TIME"])
                caption.send_keys(Keys.ENTER)
            elif elem_t.startswith("@"):
                self.browser.find_element(By.XPATH, constants["MENTION_BUTTON"]).click()
                caption.send_keys(elem_t.strip("@"))
                time.sleep(constants["USER_WAITING_TIME"])
                caption.send_keys(Keys.ENTER)
            else:
                caption.send_keys(elem_t)
                time.sleep(constants["USER_WAITING_TIME"])
         
    def __upload(self, metadata_video : dict) -> bool:
        absolute_path = os.path.join(Path().cwd(), metadata_video[constants["FILEPATH"]])
        
        time.sleep(2*constants["USER_WAITING_TIME"])
        
        iframe =self.browser.find_element(By.CSS_SELECTOR, "iframe")
        self.browser.switch_to.frame(iframe)
        time.sleep(2*constants["USER_WAITING_TIME"])
        
        self.browser.find_element(By.CSS_SELECTOR, 'input[type="file"]').send_keys(absolute_path)
        time.sleep(4*constants["USER_WAITING_TIME"])
    
        self.__inject_caption(metadata_video[constants["CAPTION"]])
        
        time.sleep(constants["USER_WAITING_TIME"])
        
        self.browser.find_element(By.XPATH, constants["POST_BUTTON"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        
        data_manager.is_published(id_table=metadata_video[constants["ID"]])
        logger.info(f"{__name__} : Video {absolute_path} uploaded to {self.dist_account[0]} on Tiktok")
        
        data_manager.remove_linked_content(metadata_video[constants["ID"]], metadata_video[constants["FILEPATH"]])

        return True
    
    
    def __bulk_upload(self, metadata_channel : list[dict]):
        for metadata_video in metadata_channel:
            if  data_manager.is_uploadable(self.dist_account[0], "tiktok", MAX_UPLOAD_DAILY=10):                   
                self.__get_to_tiktok_upload()
                self.__upload(metadata_video)
                time.sleep(3*constants["USER_WAITING_TIME"])
    
        
    def __quit(self):
        self.browser.close()
            
    def run(self):
        if data_manager.is_uploadable(self.dist_account[0], "tiktok", count = False, MAX_UPLOAD_DAILY=10):
            self.__get_driver_t()
            time.sleep(constants["USER_WAITING_TIME"])
            metadata_channel = load_metadata(self.dist_account[0], self.source_platform)    
            self.__bulk_upload(metadata_channel=metadata_channel)
            logger.info(f"{__name__} : Upload to Tiktok for {self.dist_account[0]} finished")
            self.__quit()
        else:
            logger.info(f"{__name__} : Upload to Tiktok for {self.dist_account[0]} not available")
        
if __name__ == "__main__":
    ...
        
        
        
        
        