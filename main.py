from utils import print_results
from scrape_work_ua import scrape_work_ua

query = input("Enter vacancy title to search: ").strip()
pages = int(input("Enter amount of pager to search (default = 3): ") or 3)

vacancies = scrape_work_ua(query, pages)
print_results(query, vacancies)