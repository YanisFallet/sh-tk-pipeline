"""This module implements uploading videos on YouTube via Selenium using metadata JSON file
    to extract its title, description etc."""

import os

from typing import DefaultDict, Optional, Tuple
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from collections import defaultdict
from datetime import datetime
import json
import time
from constant import Constant
from pathlib import Path
import logging
import platform

logging.basicConfig()

class YouTubeUploader:
	"""A class for uploading videos on YouTube via Selenium using metadata JSON file
	to extract its title, description etc"""

	def __init__(self, video_path: str, metadata_json_path: Optional[str] = None,
	             thumbnail_path: Optional[str] = None,
	             google_account_name : str = "shortsfactory33") -> None:
		
		#a remplacer avec arcmanager.get_ACCOUNTS
		if google_account_name in ["shortsfactory33", "yanis.fallet", "picorp696"]:
			self.google_account_name = google_account_name
		else:
			raise Exception(f"Google account {google_account_name} name not found")

		if not os.path.exists(video_path):
			raise FileNotFoundError(f'Video {video_path} file not found')
		
		self.video_path = video_path
		self.thumbnail_path = thumbnail_path

		options = uc.ChromeOptions()
		options.add_argument("--user-data-dir=/Users/yanisfallet/Library/Application Support/Google/Chrome")
		options.add_argument(f"--profile-directory={self.get_profile_path(self.google_account_name)}")

		self.browser = uc.Chrome(options=options, headless=False)

		self.logger = logging.getLogger(__name__)
		self.logger.setLevel(logging.DEBUG)
		self.__validate_inputs()

		self.is_mac = False
		if not any(os_name in platform.platform() for os_name in ["Windows", "Linux"]):
			self.is_mac = True

	def load_metadata_json(self, video_path : str):
		...
		
	def get_profile_path(self, google_account_name : str):
		with open("arc/utils/google_dir.json") as f:
			return json.load(f)[google_account_name]

	def __validate_inputs(self):
		if not self.metadata_dict[Constant.VIDEO_TITLE]:
			self.logger.warning(
				"The video title was not found in a metadata file")
			self.metadata_dict[Constant.VIDEO_TITLE] = Path(
				self.video_path).stem
			self.logger.warning("The video title was set to {}".format(
				Path(self.video_path).stem))
		if not self.metadata_dict[Constant.VIDEO_DESCRIPTION]:
			self.logger.warning(
				"The video description was not found in a metadata file")

	def upload(self):
		try:
			return self.__upload()
		except Exception as e:
			print(e)
			self.__quit()
			raise

	def __clear_field(self, field):
		field.click()
		time.sleep(Constant.USER_WAITING_TIME)
		if self.is_mac:
			field.send_keys(Keys.COMMAND + 'a')
		else:
			field.send_keys(Keys.CONTROL + 'a')
		time.sleep(Constant.USER_WAITING_TIME)
		field.send_keys(Keys.BACKSPACE)

	def __write_in_field(self, field, string, select_all=False):
		if select_all:
			self.__clear_field(field)
		else:
			field.click()
			time.sleep(Constant.USER_WAITING_TIME)

		field.send_keys(string)

	def __upload(self) -> Tuple[bool, Optional[str]]:
		edit_mode = self.metadata_dict[Constant.VIDEO_EDIT]
		if edit_mode:
			self.browser.get(edit_mode)
			time.sleep(Constant.USER_WAITING_TIME)
		else:
			self.browser.get(Constant.YOUTUBE_URL)
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.get(Constant.YOUTUBE_UPLOAD_URL)
			time.sleep(Constant.USER_WAITING_TIME)
			absolute_video_path = str(Path.cwd() / self.video_path)
			self.browser.find_element(By.XPATH, Constant.INPUT_FILE_VIDEO).send_keys(
				absolute_video_path)
			self.logger.debug('Attached video {}'.format(self.video_path))

			# Find status container
			uploading_status_container = None
			while uploading_status_container is None:
				time.sleep(5*Constant.USER_WAITING_TIME)
				uploading_status_container = self.browser.find_element(By.XPATH, Constant.UPLOADING_STATUS_CONTAINER)

		if self.thumbnail_path is not None:
			absolute_thumbnail_path = str(Path.cwd() / self.thumbnail_path)
			self.browser.find_element(By.XPATH, Constant.INPUT_FILE_THUMBNAIL).send_keys(
				absolute_thumbnail_path)
			change_display = "document.getElementById('file-loader').style = 'display: block! important'"
			self.browser.execute_script(change_display)
			self.logger.debug(
				'Attached thumbnail {}'.format(self.thumbnail_path))

		title_field, description_field = self.browser.find_elements(By.ID, Constant.TEXTBOX_ID ) #timeout=15

		title_field.clear()
		self.__write_in_field(
			title_field, self.metadata_dict[Constant.VIDEO_TITLE])
		self.logger.debug('The video title was set to \"{}\"'.format(
			self.metadata_dict[Constant.VIDEO_TITLE]))

		video_description = self.metadata_dict[Constant.VIDEO_DESCRIPTION]
		video_description = video_description.replace("\n", Keys.ENTER)
		if video_description:
			self.__write_in_field(description_field, video_description, select_all=True)
			self.logger.debug('Description filled.')

		kids_section = self.browser.find_element(By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
		kids_section.location_once_scrolled_into_view
		time.sleep(Constant.USER_WAITING_TIME)

		self.browser.find_element(By.ID, Constant.RADIO_LABEL).click()
		self.logger.debug('Selected \"{}\"'.format(Constant.NOT_MADE_FOR_KIDS_LABEL))

		# Playlist
		playlist = self.metadata_dict[Constant.VIDEO_PLAYLIST]
		if playlist:
			self.browser.find_element(By.CLASS_NAME, Constant.PL_DROPDOWN_CLASS).click()
			time.sleep(Constant.USER_WAITING_TIME)
			search_field = self.browser.find_element(By.ID, Constant.PL_SEARCH_INPUT_ID)
			self.__write_in_field(search_field, playlist)
			time.sleep(Constant.USER_WAITING_TIME * 2)
			playlist_items_container = self.browser.find_element(By.ID, Constant.PL_ITEMS_CONTAINER_ID)
			# Try to find playlist
			self.logger.debug('Playlist xpath: "{}".'.format(Constant.PL_ITEM_CONTAINER.format(playlist)))
			playlist_item = self.browser.find_element(By.XPATH, Constant.PL_ITEM_CONTAINER.format(playlist), playlist_items_container)
			if playlist_item:
				self.logger.debug('Playlist found.')
				playlist_item.click()
				time.sleep(Constant.USER_WAITING_TIME)
			else:
				self.logger.debug('Playlist not found. Creating')
				self.__clear_field(search_field)
				time.sleep(Constant.USER_WAITING_TIME)

				new_playlist_button = self.browser.find_element(By.CLASS_NAME, Constant.PL_NEW_BUTTON_CLASS)
				new_playlist_button.click()

				create_playlist_container = self.browser.find_element(By.ID, Constant.PL_CREATE_PLAYLIST_CONTAINER_ID)
				playlist_title_textbox = self.browser.find_element(By.XPATH, "//textarea", create_playlist_container)
				self.__write_in_field(playlist_title_textbox, playlist)

				time.sleep(Constant.USER_WAITING_TIME)
				create_playlist_button = self.browser.find_element(By.CLASS_NAME, Constant.PL_CREATE_BUTTON_CLASS)
				create_playlist_button.click()
				time.sleep(Constant.USER_WAITING_TIME)

			done_button = self.browser.find_element(By.CLASS_NAME, Constant.PL_DONE_BUTTON_CLASS)
			done_button.click()

		# Advanced options
		self.browser.find_element(By.ID, Constant.ADVANCED_BUTTON_ID).click()
		self.logger.debug('Clicked MORE OPTIONS')
		time.sleep(Constant.USER_WAITING_TIME)

		# Tags
		tags = self.metadata_dict[Constant.VIDEO_TAGS]
		if tags:
			# tags_container = self.browser.find_element(By.ID, Constant.TAGS_CONTAINER_ID)
			tags_field = self.browser.find_element(By.XPATH, Constant.TAGS_INPUT_V2)
			self.__write_in_field(tags_field, ','.join(tags))
			self.logger.debug('The tags were set to \"{}\"'.format(tags))


		self.browser.find_element(By.ID, Constant.NEXT_BUTTON).click()
		self.logger.debug('Clicked {} one'.format(Constant.NEXT_BUTTON))
		time.sleep(Constant.USER_WAITING_TIME)

		self.browser.find_element(By.ID, Constant.NEXT_BUTTON).click()
		self.logger.debug('Clicked {} two'.format(Constant.NEXT_BUTTON))
		time.sleep(Constant.USER_WAITING_TIME)

		self.browser.find_element(By.ID, Constant.NEXT_BUTTON).click()
		self.logger.debug('Clicked {} three'.format(Constant.NEXT_BUTTON))
		time.sleep(Constant.USER_WAITING_TIME)

		schedule = self.metadata_dict[Constant.VIDEO_SCHEDULE]
		if schedule:
			upload_time_object = datetime.strptime(schedule, "%d/%m/%Y, %H:%M")
			self.browser.find_element(By.ID, Constant.SCHEDULE_CONTAINER_ID).click()
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.find_element(By.ID, Constant.SCHEDULE_DATE_ID).click()
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.find_element(By.XPATH, Constant.SCHEDULE_DATE_TEXTBOX).clear()
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.find_element(By.XPATH, Constant.SCHEDULE_DATE_TEXTBOX).send_keys(
				datetime.strftime(upload_time_object, "%d/%m/%Y"))
			self.browser.find_element(By.XPATH, Constant.SCHEDULE_DATE_TEXTBOX).send_keys(Keys.ENTER)
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.find_element(By.XPATH, Constant.SCHEDULE_TIME).click()
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.find_element(By.XPATH, Constant.SCHEDULE_TIME).clear()
			time.sleep(Constant.USER_WAITING_TIME)
			self.browser.find_element(By.XPATH, Constant.SCHEDULE_TIME).send_keys(
				datetime.strftime(upload_time_object, "%H:%M"))
			self.browser.find_element(By.XPATH, Constant.SCHEDULE_TIME).send_keys(Keys.ENTER)
			self.logger.debug(f"Scheduled the video for {schedule}")
		else:
			public_main_button = self.browser.find_element(By.NAME, Constant.PUBLIC_BUTTON)
			self.browser.find_element(By.ID, Constant.RADIO_LABEL, public_main_button).click()
			self.logger.debug('Made the video {}'.format(Constant.PUBLIC_BUTTON))

		video_id = self.__get_video_id()
		
		#Plan

  
  		# # Check status container and upload progress
		# uploading_status_container = self.browser.find_element(By.XPATH, Constant.UPLOADING_STATUS_CONTAINER)
		# while uploading_status_container is not None:
		# 	uploading_progress = uploading_status_container.get_attribute('value')
		# 	self.logger.debug('Upload video progress: {}%'.format(uploading_progress))
		# 	time.sleep(Constant.USER_WAITING_TIME * 5)
		# 	uploading_status_container = self.browser.find_element(By.XPATH, Constant.UPLOADING_STATUS_CONTAINER)

		# self.logger.debug('Upload container gone.')

		done_button = self.browser.find_element(By.ID, Constant.DONE_BUTTON)

		# Catch such error as
		# "File is a duplicate of a video you have already uploaded"
		if done_button.get_attribute('aria-disabled') == 'true':
			error_message = self.browser.find_element(By.XPATH, Constant.ERROR_CONTAINER).text
			self.logger.error(error_message)
			return False, None

		done_button.click()
		self.logger.debug(
			"Published the video with video_id = {}".format(video_id))
		time.sleep(3*Constant.USER_WAITING_TIME)
		self.browser.find_element(By.XPATH, Constant.CLOSE_BTN).click()
		time.sleep(1100)
		return True, video_id

	def __get_video_id(self) -> Optional[str]:
		video_id = None
		try:
			video_url_container = self.browser.find_element(
				By.XPATH, Constant.VIDEO_URL_CONTAINER)
			video_url_element = self.browser.find_element(By.XPATH, Constant.VIDEO_URL_ELEMENT)
			video_id = video_url_element.get_attribute(
				Constant.HREF).split('/')[-1]
		except:
			self.logger.warning(Constant.VIDEO_NOT_FOUND_ERROR)
			pass
		return video_id

	def __quit(self):
		self.browser.close()
  
  
if __name__ == '__main__':
    y  = YouTubeUploader(
		video_path = f"content/tiktok/7276513256422821153.mp4",
		metadata_json_path = "data/metadata/met.json",
		google_account_name = "shortsfactory33"
	)
    y.upload()