import os
import sys
import time
import json
import toml
import random
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from arc_manager import ArcManagement
from abstract_scrapper import get_driver


constants = toml.load("core/facebook_uploader/constants.toml")

class FacebookUploader:
    
    def __init__(self, google_account_name: str, source_platform: str):
        self.ARC = ArcManagement(src_p=source_platform, dist_p="tiktok")
        
        if google_account_name not in self.ARC.get_google_accounts():
            raise Exception(f"Google account '{google_account_name}' name not found")

        self.google_account_name = google_account_name
        self.source_platform = source_platform
        self.dist_account = self.ARC.get_dist_by_google_account(self.google_account_name)

        if len(self.dist_account) != 1:
            raise Exception(f"Google account '{google_account_name}' is not linked to one and only one Facebook account: {len(self.dist_account)} found")
    
    def wait_randomly(self,factor : int = 1, min_time: float = constants["USER_WAITING_TIME_MIN"], max_time: float = constants["USER_WAITING_TIME_MAX"]):
        wait_time = factor * random.uniform(min_time, max_time)
        time.sleep(wait_time)
    
    def __get_driver_f(self):
        self.browser = get_driver(self.__get_profile_path(self.google_account_name), headless=False)

    def __get_profile_path(self, google_account_name: str) -> dict:
        with open('arc/utils/google_dir.json') as f:
            return json.load(f)[google_account_name]
        
    def __go_to_facebook_upload(self):
        self.browser.get(constants["FACEBOOK_CREATOR_CENTER"])
        self.wait_randomly()
        
        
    def run(self):
        self.__get_driver_f()
        self.__go_to_facebook_upload()
        self.wait_randomly()
        self.browser.quit()
        
        
if __name__ == "__main__":
    facebook_uploader = FacebookUploader("picorp", "tiktok")
    facebook_uploader.run()
