import os
import time
import random

import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service


from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


def get_driver(profile = None, headless = False):
    if profile is not None: 
        print(f"Using profile {profile}")
        if profile not in ["Default", "Profile 4", "Profile 3"]:
            raise Exception("Profile must be 'Default', 'Profile 3' or 'Profile 4'")
        else:
            s = Service('/Users/yanisfallet/Downloads/chromedriver')
            options = uc.ChromeOptions()
            options.add_argument(f"--user-data-dir=/Users/yanisfallet/Library/Application Support/Google/Chrome")
            options.add_argument(f"--profile-directory={profile}")
            return uc.Chrome(options=options, headless=headless)
    else:
        return uc.Chrome(headless=headless)
    

class AbstractScrapper:
    def __init__(self, channel_name, content_name : str, dist_platform :str, pool):
        self.channel_name = channel_name
        self.content_name = content_name
        self.pool = pool
        self.dist_platform = dist_platform

        if not os.path.exists(os.path.join("content", self.content_name)):
            os.makedirs(os.path.join("content", self.content_name))

    def get_headers(self):
        software_names = [SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=10)
        user_agent = user_agent_rotator.get_random_user_agent()
        return {"User-Agent" : user_agent}

    def scroll_page_to_the_end(self, driver):
        old_position = 0
        new_position = None
        while new_position != old_position:
            old_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                " window.pageYOffset : (document.documentElement ||"
                " document.body.parentNode || document.body);"))
            time.sleep(random.uniform(0.5, 1.5))
            driver.execute_script((
                "var scrollingElement = (document.scrollingElement ||"
                " document.body);scrollingElement.scrollTop ="
                " scrollingElement.scrollHeight;"))
            new_position = driver.execute_script(
                ("return (window.pageYOffset !== undefined) ?"
                " window.pageYOffset : (document.documentElement ||"
                " document.body.parentNode || document.body);"))
        
    