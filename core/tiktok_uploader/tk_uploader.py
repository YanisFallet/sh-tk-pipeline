import os
import sys
import time
import json
import toml
import logging
from pathlib import Path

from selenium.webdriver.common.by import By

from metadata import load_metadata

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import data_manager
from abstract_scrapper import get_driver
from arc_manager import ArcManagement

constants = toml.load("core/tiktok_uploader/constants.toml")

class TiktokUplaoder:
    
    def __init__(self, 
                google_account_name : str,
                source_platform : str):
    
        if not google_account_name in ["shortsfactory33", "yanis.fallet", "picorp696"]:
            raise Exception(f"Google account '{google_account_name}' name not found")
            
        self.google_account_name = google_account_name
        self.source_platform = source_platform

    def __get_driver_t(self):
        self.browser = get_driver(self.__get_profile_path(self.google_account_name), headless = False)
        
    def __get_profile_path(self, google_account_name : str) -> dict:
        with open('arc/utils/google_dir.json') as f:
            return json.load(f)[google_account_name]
        
    def __get_to_tiktok_upload(self):
        self.browser.get(constants["TIKTOK_CREATOR_CENTER"])
        time.sleep(constants["USER_WAITING_TIME"])
         
    def __upload(self, metadata_video : dict) -> bool:
        absolute_path = os.path.join(Path().cwd(), metadata_video[constants["FILEPATH"]])
        
        self.browser.find_element(By.CSS_SELECTOR, constants["UPLOAD_CONTAINER_CSS_SELECTOR"]).send_keys(
            absolute_path
        )
        logging.info(f"Attached Video {absolute_path}")
        time.sleep(constants["USER_WAITING_TIME"])
        
        self.browser.find_element(By.XPATH, constants["CAPTION_INPUT"]).send_keys(
            metadata_video[constants["CAPTION_CONTENT"]]
        )
        time.sleep(constants["USER_WAITING_TIME"])
        
        self.browser.find_element(By.XPATH, constants["POST_BUTTON"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        
        data_manager.is_published(id_filename=metadata_video[constants["ID_FILENAME"]])
        
        os.remove(absolute_path)
        
        return True
    
    
    def __bulk_upload(self, metadata_channel : list[dict]):
        for metadata_video in metadata_channel:
            self.__get_to_tiktok_upload()
            self.__upload(metadata_video)
            time.sleep(constants["USER_WAITING_TIME"])
            
    def __quit(self):
        self.browser.quit()
            
    def run(self):
        self.__get_driver_t()
        self.__bulk_upload()
        self.__quit()
        

        
        
        
        
        