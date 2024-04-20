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

from tiktok_uploader.metadata import load_metadata
# from metadata import load_metadata

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils
import data_manager
from abstract_scrapper import get_driver
from arc_manager import ArcManagement
from logging_config import logger

constants = toml.load("core/tiktok_uploader/constants.toml")

class TiktokUploader:
    def __init__(self, google_account_name: str, source_platform: str):
        if google_account_name not in ["shortsfactory33", "yanis.fallet", "picorp696"]:
            raise Exception(f"Google account '{google_account_name}' name not found")

        self.ARC = ArcManagement(src_p=source_platform, dist_p="tiktok")
        self.google_account_name = google_account_name
        self.source_platform = source_platform
        self.dist_account = self.ARC.get_dist_by_google_account(self.google_account_name)

        if len(self.dist_account) != 1:
            raise Exception(f"Google account '{google_account_name}' is not linked to one and only one Tiktok account: {len(self.dist_account)} found")

    def __get_driver_t(self):
        self.browser = get_driver(self.__get_profile_path(self.google_account_name), headless=False)

    def __get_profile_path(self, google_account_name: str) -> dict:
        with open('arc/utils/google_dir.json') as f:
            return json.load(f)[google_account_name]

    def __get_to_tiktok_upload(self):
        self.browser.get(constants["TIKTOK_CREATOR_CENTER"])
        self.wait_randomly()
    
    def __move_mouse_randomly(self):
        actions = ActionChains(self.browser)
        width = self.browser.execute_script("return document.body.clientWidth;")
        height = self.browser.execute_script("return document.body.clientHeight;")
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        actions.move_to_element_with_offset(self.browser.find_element_by_tag_name("body"), x, y).perform()
        self.wait_randomly()
        
    def wait_randomly(self,factor : int = 1, min_time: float = constants["USER_WAITING_TIME_MIN"], max_time: float = constants["USER_WAITING_TIME_MAX"]):
        wait_time = factor * random.uniform(min_time, max_time)
        time.sleep(wait_time)


    def __inject_caption(self, text: str, caption_input_xpath):
        split_text = utils.split_text_m_h_t(text)
        
        i = 0
        found = False
        while i < 100 and not found:
            try:
                caption = self.browser.find_element(By.XPATH, caption_input_xpath)
                found = True
            except NoSuchElementException:
                self.wait_randomly()
                i += 1
        
        ActionChains(self.browser).move_to_element(caption).click(caption).key_down(Keys.COMMAND).send_keys('a').key_up(Keys.COMMAND).send_keys(Keys.BACK_SPACE).perform()
        self.wait_randomly()
        
        for elem_t in split_text:
            if elem_t.startswith("#") or elem_t.startswith("@"):
                ActionChains(self.browser).send_keys(elem_t).perform()
                self.wait_randomly(0.2)
                ActionChains(self.browser).send_keys(Keys.RETURN).perform()
                self.wait_randomly(0.2)
            else:
                ActionChains(self.browser).send_keys(elem_t).perform()
                self.wait_randomly(0.2)
                
    def __upload(self, metadata_video: dict):
        self.__get_to_tiktok_upload()
        
        absolute_path = os.path.join(Path().cwd(), metadata_video[constants["FILEPATH"]])

        self.wait_randomly(factor= 2)

        iframe = self.browser.find_element(By.CSS_SELECTOR, "iframe")
        self.browser.switch_to.frame(iframe)
        self.wait_randomly(factor= 2)

        self.browser.find_element(By.CSS_SELECTOR, 'input[type="file"]').send_keys(absolute_path)

        self.__inject_caption(metadata_video[constants["CAPTION"]], constants["CAPTION_INPUT"])

        self.wait_randomly(factor= 2)

        self.browser.find_element(By.XPATH, constants["POST_BUTTON"]).click()
        self.wait_randomly()
        
        data_manager.is_published(id_table=metadata_video[constants["ID"]])
        logger.info(f"{__name__}: Video {absolute_path} uploaded to {self.dist_account[0]} on Tiktok")
        data_manager.remove_linked_content(metadata_video[constants["ID"]], metadata_video[constants["FILEPATH"]])

        self.__wait_tiktok_modal()
        
        self.wait_randomly()
        
        return True

    def __wait_tiktok_modal(self):
        found = False
        while not found:
            try:
                logger.info(f"{__name__}: Waiting for modal for {self.dist_account[0]} on Tiktok")
                self.browser.find_element(By.XPATH, constants["MODAL_BTN"])
                found = True
            except:
                self.wait_randomly()

        self.browser.find_element(By.XPATH, constants["MODAL_BTN"]).click()
        logger.info(f"{__name__}: Modal clicked")
        self.wait_randomly()

    def __quit(self):
        self.browser.close()

    def __bulk_upload(self, metadata_channel : list[dict]):
        for metadata_video in metadata_channel:
            if  data_manager.is_uploadable(self.dist_account[0], "tiktok", MAX_UPLOAD_DAILY=10):                   
                self.__get_to_tiktok_upload()
                self.__upload(metadata_video)
                self.wait_randomly()
    
    def run(self):
        for dist_account in self.dist_account:
            if data_manager.is_uploadable(dist_account, "tiktok", count = False, MAX_UPLOAD_DAILY=10):
                print("inside")
                self.__get_driver_t()
                self.wait_randomly()
                print("wait")
                metadata_channel = load_metadata(dist_account, "tiktok")
                print(metadata_channel)
                self.__bulk_upload(metadata_channel=metadata_channel)
                logger.info(f"{__name__} : Upload to Tiktok for {dist_account} finished")
                self.__quit()
            else:
                logger.info(f"{__name__} : Upload to Tiktok for {dist_account} not available")
        
if __name__ == "__main__":
    uploader = TiktokUploader(
        google_account_name = "shortsfactory33",
        source_platform = "instagram"
    )
    print(uploader.dist_account)
    
    # uploader.run()
    
    
