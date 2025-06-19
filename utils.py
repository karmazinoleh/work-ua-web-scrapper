import requests
from bs4 import BeautifulSoup
import re
import statistics
from urllib.parse import quote_plus
from dataclasses import dataclass
from typing import List, Optional, Union, Tuple

def extract_salary(text: str) -> Union[int, Tuple[int, int], None]:
    if "грн" not in text:
        return None

    clean_text = re.sub(r"[\u202F\u00A0\u2009]", " ", text)

    # Pattern for salary range ("50 000 – 120 000 грн")
    range_pattern = re.search(r"(\d[\d ]+)\s*[-–]\s*(\d[\d ]+)\s*грн", clean_text)
    if range_pattern:
        salary_from = int(range_pattern.group(1).replace(" ", ""))
        salary_to = int(range_pattern.group(2).replace(" ", ""))
        return salary_from, salary_to

    # Pattern for single value ("30 000 грн")
    single_pattern = re.search(r"(\d[\d ]+)\s*грн", clean_text)
    if single_pattern:
        salary = int(single_pattern.group(1).replace(" ", ""))
        return salary

    return None

def calculate_salary_statistics(vacancies) -> dict:
        """Calculate salary statistics"""
        salaries = []
        
        for vacancy in vacancies:
            if vacancy.salary_min and vacancy.salary_max:
                avg_salary = (vacancy.salary_min + vacancy.salary_max) / 2
                salaries.append(avg_salary)
            elif vacancy.salary_min:
                salaries.append(vacancy.salary_min)
            elif vacancy.salary_max:
                salaries.append(vacancy.salary_max)
        
        if not salaries:
            return {
                'median': None,
                'mean': None,
                'min': None,
                'max': None,
                'count': 0,
                'total_vacancies': len(vacancies)
            }
        
        return {
            'median': statistics.median(salaries),
            'mean': statistics.mean(salaries),
            'min': min(salaries),
            'max': max(salaries),
            'count': len(salaries),
            'total_vacancies': len(vacancies)
        }

def print_results(query: str, vacancies) -> None:
        """Виведення результатів"""
        stats = calculate_salary_statistics(vacancies)
        
        print(f"\n{'='*60}")
        print(f"RESULTS FOR: '{query}'")
        print(f"{'='*60}")
        
        print(f"Found vacancies: {stats['total_vacancies']}")
        print(f"Vacancies with a salary: {stats['count']}")
        
        if stats['median']:
            print(f"\nSTATISTICS OF SALARIES:")
            print(f"Median: {stats['median']:,.0f} грн")
            print(f"Avarage: {stats['mean']:,.0f} грн")
            print(f"Minimum: {stats['min']:,.0f} грн")
            print(f"Maximum: {stats['max']:,.0f} грн")
        else:
            print("\nNo salary data available.")
        
        print(f"\n10 VACANCIES:")
        print("-" * 60)
        
        for i, vacancy in enumerate(vacancies[:10], 1):
            salary_info = ""
            if vacancy.salary_min and vacancy.salary_max:
                salary_info = f"{vacancy.salary_min:,}-{vacancy.salary_max:,} грн"
            elif vacancy.salary_min:
                salary_info = f"від {vacancy.salary_min:,} грн"
            elif vacancy.salary_max:
                salary_info = f"до {vacancy.salary_max:,} грн"
            else:
                salary_info = "Salary not specified"
            
            print(f"{i:2d}. {vacancy.title}")
            print(f"    COMPANY: {vacancy.company}")
            print(f"    SALARY: {salary_info}")
            print(f"    LOCATION: {vacancy.location}")
            print(f"    SOURCE: {vacancy.source}")
            print(f"    URL: {vacancy.url}")
            print()
