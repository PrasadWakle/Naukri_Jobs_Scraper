from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import logging
import time
import traceback
import sys
from pprint import pprint

class Naukri_Scraper:
    def __init__(self, designation):
        self.designation = designation


    def scrap_jobs(self):

        try:
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)

            logging_format=logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')

            file_handler=logging.FileHandler('naukri.com_log.log')
            file_handler.setFormatter(logging_format)

            logger.addHandler(file_handler)
        
            url = "https://www.naukri.com/"

            # Install ChromeDriver and initialize driver variable
            driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
            logger.info("Successfully istalled the webdriver!")
            
            driver.maximize_window()
            driver.implicitly_wait(10)

            # Load the naukri.com url
            driver.get(url)
            logger.info(f"URL loaded successfully!")

            # Selecting search box of naurki.com and entering designation
            searchBox = driver.find_element(By.CSS_SELECTOR, ".suggestor-input")
            searchBox.send_keys(self.designation)
            time.sleep(2)

            # Selecting the experience as fresher
            select_exp = driver.find_element(By.CSS_SELECTOR, ".dropdownMainContainer")
            select_exp.click()
            drop_down = driver.find_element(By.CSS_SELECTOR, ".dropdownContainer")
            ul_element = drop_down.find_element(By.CSS_SELECTOR, ".dropdown ")
            li_element = ul_element.find_element(By.XPATH, "//li[@value = '#0']")
            li_element.click()
            time.sleep(2)

            # Code to select search button and click on it
            submit = driver.find_element(By.CSS_SELECTOR, ".qsbSubmit")
            submit.click()
            logger.info(f"Successfully submitted the designation and experience.")

            # List to store the job inforamtion
            job_info = []

            for i in range(2):

                job_listings = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@class='cust-job-tuple layout-wrapper lay-2 sjw__tuple ']"))
                )

                # For loop to go through each job listing and scrap it's data
                for job in job_listings:
                    try:
                        job_title = job.find_element(
                            By.XPATH, ".//div[@class=' row1']/a[@class='title ']"
                        )
                        job_title_text = job_title.text # Job Title e.g., Data Scientist
                        job_link = job_title.get_attribute("href")

                        company_name = job.find_element(
                            By.CSS_SELECTOR,
                            ".comp-name",
                        ).text # Company Name e.g., Amazon

                        # Some companies do not have ratings. Try Except block to avoid errors.
                        try:
                            company_rating = job.find_element(
                                By.XPATH,
                                ".//div[@class=' row2']//span[@class='main-2']",
                            ).text # Company Rating e.g., 4.2
                           
                        except NoSuchElementException:
                            logger.info(f"No rating found for the company: {company_name}")
                            company_rating = None
                            pass


                        try:
                            total_reviews = job.find_element(
                            By.XPATH,
                            ".//div[@class=' row2']//a[@class=' review ver-line']",
                        ).text # Company Reviews e.g., 14 Reviews

                        except NoSuchElementException:
                            logger.info(f"No reviews found for the company:{company_name}")
                            total_reviews = None
                            pass
                                      

                        job_details = job.find_element(
                            By.XPATH, ".//div[@class=' row3']/div[@class='job-details ']"
                        )
                        reqd_exp = job_details.find_element(
                            By.XPATH, ".//span[@class='expwdth']"
                        ).text # Required Experience e.g., 0-4 years
                        

                        ctc = job_details.find_element(By.XPATH,".//span[@class='ni-job-tuple-icon ni-job-tuple-icon-srp-rupee sal']/span").text # CTC e.g., 3.5 LPA

                        
                        try:
                            location = job_details.find_element(By.XPATH,".//span[@class='locWdth' or class='locWdth2']").text # Job Location e.g., Mumbai
                        except NoSuchElementException:   
                            logger.info(f"Job location not given for the post of:{job_title_text}")
                            location = None
                            pass

                        # Scraping required skills for the job
                        req_skills = job.find_elements(By.XPATH,".//div[@class=' row5']/ul[@class='tags-gt ']/li[@class='dot-gt tag-li ']")
                        skills_list = []
                        for skill in req_skills:
                            skill_text = skill.get_attribute("innerText")

                            if skill_text != None:
                                skills_list.append(skill_text)
                        
                        # Scraping the date when the job was posted
                        job_posted = job.find_element(By.CSS_SELECTOR,".job-post-day ").text

                        # Dictionary to store the job information
                        job_dict = {
                            "job_title": job_title_text,
                            "company_name": company_name,
                            "company_rating":company_rating,
                            "total_reviews":total_reviews,
                            "experience": reqd_exp,
                            "ctc": ctc,
                            "location": location,
                            "posted_date": job_posted,
                            "skills": skills_list,
                            "job_link":job_link
                        }

                    except NoSuchElementException as e:
                        exc_type, exc_value, exc_traceback = sys.exc_info()
                        logger.error("Exception type: ", exc_type)
                        logger.error("Exception message: ", exc_value)
                        logger.error("Exception occurred on line: ", traceback.tb_lineno(exc_traceback))
                        continue  # Move to the next iteration of the loop

                    job_info.append(job_dict)
                    
                    try:
                        next_page = driver.find_element(By.CSS_SELECTOR,".styles_btn-secondary__2AsIP")
                        logger.info("Going to next page.")
                        next_page.click()
                    except:
                        logger.info("All job listings caught up.")
                    
            return job_info

        except NoSuchElementException:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error("Exception type: ", exc_type)
            logger.error("Exception message: ", exc_value)
            logger.error("Exception occurred on line: ", traceback.tb_lineno(exc_traceback))
            
        finally:
            logger.info("Closing the driver.")
            # Close the driver
            driver.quit()

