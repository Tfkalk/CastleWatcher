from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth
from bs4 import BeautifulSoup
import sys
from enum import Enum

# class Museum(Enum):
# # 	AIB = 
# 	NASM = 
# 	HIRSCHHORN = 
# 	CASTLE =
# 	AFRICAN = 
# 	SACKLER =
# 	FREER =
# 	NATHIST = 
# 	AMHIST =
# 	SAAM = 
# 	NPG =
# 	NPM = 
# 	ZOO = 
# 	ACM =

def query_museum_upcoming(museum_uuid) -> None:
	with Stealth().use_sync(sync_playwright()) as p:
		browser = p.chromium.launch()
		page = browser.new_page()
		page.goto(f'https://www.si.edu/exhibitions/upcoming?edan_fq[0]=p.event.location.extended.location_id:"p1b-1474716020541-{museum_uuid}-0"')
		page.wait_for_selector(".c-exhibition-teaser__inner-wrap", timeout=30000)
		soup = BeautifulSoup(page.content(), "html.parser")
		browser.close()

	for item in soup.select(".c-exhibition-teaser__inner-wrap"):
		title = item.select_one(".c-exhibition-teaser__title-link .text").get_text(strip=True)
		date = item.select_one(".c-exhibition-teaser__date").get_text(strip=True)
		print(f"{title} — {date}")

def main():
	query_museum_upcoming("1475754368943")

if __name__ == "__main__":
    sys.exit(main())

"""
NASM: 1475754763122
SACKLER: 1475754368943
AMHIST: 1475755303891
"""

# https://www.si.edu/exhibitions?edan_fq%5B0%5D=p.event.location.extended.location_id%3A%22p1b-1474716020541-1475754763122-0%22