import requests
from bs4 import BeautifulSoup
import re
import statistics
import time
import json
from urllib.parse import quote_plus
from dataclasses import dataclass
from typing import List, Optional, Union, Tuple
import logging
from utils import extract_salary, calculate_salary_statistics, print_results

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

vacancies = []

session = requests.Session()
session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

@dataclass
class JobVacancy:
    title: str
    company: str
    salary_min: Optional[int]
    salary_max: Optional[int]
    location: str
    url: str
    source: str

def scrape_work_ua(query: str, pages: int = 3) -> List[JobVacancy]:
        """Scrap Work.ua"""
        logger.info(f"Scrapping Work.ua for query: {query}")
        vacancies = []
        
        for page in range(1, pages + 1):
            try:
                url = f"https://www.work.ua/jobs/?search={quote_plus(query)}&page={page}"
                response = session.get(url, timeout=10)
                
                if response.status_code != 200:
                    logger.warning(f"Error {page} from Work.ua: {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_items = soup.find_all('div', class_='job-link')
                #print(job_items[1])
                for item in job_items:
                    #logger.info(f"Processing item: {item}")
                    try:
                        # Name of the job
                        title_elem = item.find('h2')
                        if title_elem:
                            link_elem = title_elem.find('a')
                            title = link_elem.get_text(strip=True) if link_elem else "N/A"
                            job_url = "https://www.work.ua" + link_elem.get('href') if link_elem else ""
                        else:
                            title = "N/A"
                            job_url = ""
                        
                        # Company name
                        mt_xs_div = item.find('div', class_='mt-xs')
                        company_elem = None
                        if mt_xs_div:
                             span_mr_xs = mt_xs_div.find('span', class_='mr-xs')
                             if span_mr_xs:
                                inner_span = span_mr_xs.find('span')
                                if inner_span:
                                    company_elem = inner_span
                        #logger.info(f"\n\n\nCompany element: {company_elem} \n\n\n")
                        company = company_elem.get_text(strip=True) if company_elem else "N/A"
                        #logger.info(f"Company element: {company}")

                        # Salary
                        salary_elem = item.find('span', class_='strong-600')
                        #logger.info(f"\n\n\nSalary element: {salary_elem}")
                        salary_text = salary_elem.get_text(strip=True)
                        salary = extract_salary(salary_text)
                        #logger.info(f"Salary: {salary}\n")
                        if salary is None:
                            salary_min, salary_max = None, None
                        elif isinstance(salary, int):
                            salary_min = salary
                            salary_max = salary
                        else:
                            salary_min, salary_max = salary[0], salary[1]
                        #logger.info(f"\n\n\nSalary: {salary_min}, or {salary_max}\n\n\n")
                        
                        # Локація
                        location_elem = item.find('div', class_='mt-xs').find('span', class_="")
                        #logger.info(f"\n\n\nLocation element: {location_elem}")
                        location = location_elem.get_text(strip=True) if location_elem else "N/A"
                        
                        vacancy = JobVacancy(
                            title=title,
                            company=company,
                            salary_min=salary_min,
                            salary_max=salary_max,
                            location=location,
                            url=job_url,
                            source="Work.ua"
                        )
                        vacancies.append(vacancy)
                        
                    except Exception as e:
                        logger.error(f"Error while processing vacancy from Work.ua: {e}")
                        continue
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error when scrapping Work.ua on page {page}: {e}")
                continue
        
        logger.info(f"Found {len(vacancies)} vacancies on Work.ua")
        return vacancies