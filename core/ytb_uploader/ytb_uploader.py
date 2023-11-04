import os
import sys
import time
import json
import toml
import platform
from datetime import datetime
from pathlib import Path

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from ytb_uploader.metadata import load_metadata


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import utils
import arc_manager
import data_manager
from abstract_scrapper import get_driver
from logging_config import logger

constants = toml.load("core/ytb_uploader/constants.toml")

class YoutubeUploader:
    
    def __init__(self,
                 google_account_name : str,
                 source_platform : str):
        
        if not google_account_name in ["shortsfactory33", "yanis.fallet", "picorp696"]:
            raise Exception(f"Google account '{google_account_name}' name not found")
            
        self.ARC = arc_manager.ArcManagement(src_p=source_platform, dist_p="youtube")
        
        self.google_account_name : str = google_account_name
        self.all_dist_accounts : list = self.ARC.get_dist_by_google_account(self.google_account_name)
        
        self.is_mac = False
        if not any(os_name in platform.platform() for os_name in ["Windows", "Linux"]):
            self.is_mac = True
            
    def get_driver_y(self):
        self.browser = get_driver(self.__get_profile_path(self.google_account_name), headless = False)
        
    def __get_profile_path(self, google_account_name : str):
        with open('arc/utils/google_dir.json') as f:
            return json.load(f)[google_account_name]
        
    def __clear_field(self, field : uc.WebElement):
        field.click()
        time.sleep(constants["USER_WAITING_TIME"])
        if self.is_mac:
            field.send_keys(Keys.COMMAND + "a")
        else:
            field.send_keys(Keys.CONTROL + "a")
        time.sleep(constants["USER_WAITING_TIME"])
        field.send_keys(Keys.BACKSPACE)
    
    def __write_in_field(self, field : uc.WebElement, string : str, select_all : bool = False):
        if select_all:
            self.__clear_field(field)
        else : 
            field.click()
            time.sleep(constants["USER_WAITING_TIME"])
        field.send_keys(string)
        
    def __go_to_ytb_studio(self):
        self.browser.get(constants["YOUTUBE_URL"])
        time.sleep(constants["USER_WAITING_TIME"])
        self.browser.get(constants["YOUTUBE_STUDIO_URL"])
        
    def __get_which_channel(self):
        self.browser.find_element(By.XPATH, constants["ACCOUNT_IMG"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        name = self.browser.find_element(By.XPATH, constants["CHANNEL_NAME"]).text
        self.browser.find_element(By.XPATH, constants["ACCOUNT_IMG"]).click()
        return name
        
    def __switch_channel(self, target_name : str):
        self.browser.find_element(By.XPATH, constants["ACCOUNT_IMG"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        self.browser.find_element(By.XPATH, constants["CHANGE_ACCOUNT"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        
        nb_accounts = len(self.browser.find_elements(By.XPATH, constants["ACCOUNTS"]))
        i = 1
        found = False
        while i <= nb_accounts and not found:
            channel_title = self.browser.find_element(By.XPATH, constants["RIGHT_CHANNEL"] + f"[{i}]" + constants["CHANNEL_TITLE"])
            if channel_title.text == target_name:
                found = True
                self.browser.find_element(By.XPATH, constants["RIGHT_CHANNEL"] + f"[{i}]").click()
                time.sleep(constants["USER_WAITING_TIME"])
            i += 1
        
        return found
    
    def __upload(self, video_path : str, video_metadata : dict):
        
        video_metadata[constants["VIDEO_SCHEDULE"]] = data_manager.schedule_video(
            dist_account = video_metadata[constants["VIDEO_ACCOUNT"]],
            platform = "youtube",
            id_table=video_metadata["id"]
        )
        
        absolute_path_video = os.path.join(Path.cwd(), video_path)
        

        time.sleep(constants["USER_WAITING_TIME"])
        
        self.browser.get(constants["YOUTUBE_UPLOAD_URL"])
        time.sleep(constants["USER_WAITING_TIME"])
        self.browser.find_element(By.XPATH, constants["INPUT_FILE_VIDEO"]).send_keys(absolute_path_video)
        logger.info(f"{__name__} : Attached Video {video_path}")
        time.sleep(constants["USER_WAITING_TIME"])
        
        uploading_status_container = None
        while uploading_status_container is None:
            time.sleep(constants["USER_WAITING_TIME"])
            uploading_status_container = self.browser.find_element(By.XPATH, constants["UPLOADING_STATUS_CONTAINER"])
            
        title_field, description_field = self.browser.find_elements(By.ID, constants["TEXTBOX_ID"])
        
        title_field.clear()
        
        self.__write_in_field(title_field, video_metadata[constants["VIDEO_TITLE"]])
        logger.info(f"{__name__} : Title {video_metadata[constants['VIDEO_TITLE']]}")
        time.sleep(constants["USER_WAITING_TIME"])
        
        video_description = video_metadata[constants["VIDEO_DESCRIPTION"]].replace("\n", Keys.ENTER)
        if video_description:
            self.__write_in_field(description_field, video_description)
            logger.info(f"{__name__} : Description {video_description}")
            time.sleep(constants["USER_WAITING_TIME"])
        
        kids_section = self.browser.find_element(By.NAME, constants["NOT_MADE_FOR_KIDS_LABEL"])
        kids_section.location_once_scrolled_into_view
        time.sleep(constants["USER_WAITING_TIME"])
        self.browser.find_element(By.ID, constants["RADIO_LABEL"]).click()
        
        self.browser.find_element(By.ID, constants["ADVANCED_BUTTON_ID"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        
        tags = video_metadata[constants["VIDEO_TAGS"]]
        time.sleep(constants["USER_WAITING_TIME"])
        if tags:
            tags_field = self.browser.find_element(By.XPATH, constants["TAGS_INPUT_V2"])
            tags_field.location_once_scrolled_into_view
            self.__write_in_field(tags_field, tags)
            logger.info(f"{__name__} : Tags {tags}")
            time.sleep(constants["USER_WAITING_TIME"])
        
        self.browser.find_element(By.ID, constants["NEXT_BUTTON"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        self.browser.find_element(By.ID, constants["NEXT_BUTTON"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        self.browser.find_element(By.ID, constants["NEXT_BUTTON"]).click()
        time.sleep(constants["USER_WAITING_TIME"])
        
        schedule = video_metadata[constants["VIDEO_SCHEDULE"]]
        
        if schedule is not None:
            upload_time_object = datetime.strptime(schedule, "%Y-%m-%d %H:%M:%S")
            self.browser.find_element(By.ID, constants["SCHEDULE_CONTAINER_ID"]).click()
            self.browser.find_element(By.ID, constants["SCHEDULE_DATE_ID"]).click()
            self.browser.find_element(By.XPATH, constants["SCHEDULE_DATE_TEXTBOX"]).clear()
            self.browser.find_element(By.XPATH, constants["SCHEDULE_DATE_TEXTBOX"]).send_keys(
                datetime.strftime(upload_time_object, "%d/%m/%Y"))
            self.browser.find_element(By.XPATH, constants["SCHEDULE_DATE_TEXTBOX"]).send_keys(Keys.ENTER)
            logger.info(f"{__name__} : Schedule set to {schedule}")
        else: 
            public_main_button = self.browser.find_element(By.NAME, constants["PUBLIC_BUTTON"])
            self.browser.find_element(By.ID, constants["RADIO_LABEL"]).click()
            
            
        time.sleep(constants["USER_WAITING_TIME"])
            
        done_button = self.browser.find_element(By.ID, constants["DONE_BUTTON"])
        
        if done_button.get_attribute("aria-disabled") == "true":
            error_message = self.browser.find_element(By.XPATH, constants["ERROR_CONTAINER"]).text
            logger.info(f"{__name__} : Error message : {error_message}")
            return False
        
        done_button.click()
        time.sleep(2*constants["USER_WAITING_TIME"])
        self.browser.find_element(By.XPATH, constants["CLOSE_BTN"]).click()
        logger.info(f"{__name__} : Published the video {video_path} on Youtube")
        data_manager.is_published(id_table=video_metadata["id"])

        data_manager.is_removable(filepath=video_path)
        
        return True
    
    def __bulk_upload(self, metadata_channel : list[dict]):
        i = 0
        while i < len(metadata_channel) and data_manager.is_uploadable(metadata_channel[i][constants["VIDEO_PATH"]], platform="youtube", count = True):
            self.__upload(metadata_channel[i][constants["VIDEO_PATH"]], metadata_channel[i])
            time.sleep(3*constants["USER_WAITING_TIME"])
            i+=1
            
    def __minimum_upload(self, metadata_channel : list[dict]):
        return len(metadata_channel) > constants["MIN_VIDEOS_TO_UPLOAD"]

        
    def run(self):
        must_run  = [data_manager.is_uploadable(dist_account, platform="youtube", count = False) for dist_account in self.all_dist_accounts]
        
        if any(must_run):
            #initialize browser
            self.get_driver_y()
            #go to youtube studio
            time.sleep(constants["USER_WAITING_TIME"])
            self.__go_to_ytb_studio()
            time.sleep(constants["USER_WAITING_TIME"])
            #current channel situation
            current_channel = self.__get_which_channel()
            time.sleep(constants["USER_WAITING_TIME"])
            metadata_channel = load_metadata(dist_account = current_channel, platform="youtube")

            if self.__minimum_upload(metadata_channel=metadata_channel) and data_manager.is_uploadable(current_channel, platform="youtube", count = False):
                self.__bulk_upload(metadata_channel)
                data_manager.update_one_dist(dist_account = current_channel, platform = "youtube")
            
            self.all_dist_accounts.remove(current_channel)
            for channel in self.all_dist_accounts:
                metadata_channel = load_metadata(dist_account = channel, platform="youtube")
                
                if self.__minimum_upload(metadata_channel=metadata_channel) and data_manager.is_uploadable(channel, platform="youtube", count = False):
                    switched = self.__switch_channel(channel)
                    if switched:
                        self.__bulk_upload(metadata_channel)
                        data_manager.update_one_dist(dist_account = channel, platform = "youtube")

            self.__quit()
    
    def __quit(self):
        self.browser.quit()