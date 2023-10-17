import os
import sys
import time
import json
import logging
from pathlib import Path

from selenium.webdriver.common.by import By

from constant import Constant
from metadata import load_metadata

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import data_manager
from abstract_scrapper import get_driver
from arc_manager import ArcManagement



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
        self.browser.get(Constant.TIKTOK_CREATOR_CENTER)
        time.sleep(Constant.USER_WAINTING_TIME)
         
    def __upload(self, metadata_video : dict) -> bool:
        absolute_path = os.path.join(Path().cwd(), metadata_video[Constant.FILEPATH])
        
        self.browser.find_element(By.CSS_SELECTOR, Constant.UPLOAD_CONTAINER_CSS_SELECTOR).send_keys(
            absolute_path
        )
        logging.info(f"Attached Video {absolute_path}")
        time.sleep(Constant.USER_WAINTING_TIME)
        
        self.browser.find_element(By.XPATH, Constant.CAPTION_INPUT).send_keys(
            metadata_video[Constant.CAPTION_CONTENT]
        )
        time.sleep(Constant.USER_WAINTING_TIME)
        
        self.browser.find_element(By.XPATH, Constant.POST_BUTTON).click()
        time.sleep(Constant.USER_WAINTING_TIME)
        
        data_manager.is_published(id_filename=metadata_video[Constant.ID_FILENAME])
        
        os.remove(absolute_path)
        
        return True
    
    
    def __bulk_upload(self, metadata_channel : list[dict]):
        for metadata_video in metadata_channel:
            self.__get_to_tiktok_upload()
            self.__upload(metadata_video)
            time.sleep(Constant.USER_WAINTING_TIME)
            
    def __quit(self):
        self.browser.quit()
            
    def run(self):
        self.__get_driver_t()
        self.__bulk_upload()
        self.__quit()
        

        
        
        
        
        