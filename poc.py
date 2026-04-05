from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth
from bs4 import BeautifulSoup
import sys
from enum import Enum
import time
	
class Museum:
	def __init__(self, name, uuid, check=True):
		self.name = name
		self.uuid = uuid
		self.check = check
		self.future_exhibits = []
		
	def add_future_exhibits(self, exhibits):
		self.future_exhibits.append(exhibits)
		
	def __str__(self):
		return f"{self.name}"
	
class Exhibit:
	def __init__(self, name, from_date, to_date):
		self.name = name
		self.from_date = from_date
		self.to_date = to_date
		
	def __str__(self):
		return f"{self.name}: ({self.from_date} - {self.to_date})"
		
	def __repr__(self):
	    return str(self)
	
def query_museum_upcoming(museum_uuid) -> list:
	with Stealth().use_sync(sync_playwright()) as p:
		browser = p.chromium.launch()
		page = browser.new_page()
		page.goto(f'https://www.si.edu/exhibitions/upcoming?edan_fq[0]=p.event.location.extended.location_id:"p1b-1474716020541-{museum_uuid}-0"')
		page.wait_for_selector(".c-exhibition-teaser__inner-wrap", timeout=15000)
		soup = BeautifulSoup(page.content(), "html.parser")
		browser.close()
		
	exhibits = []

	for item in soup.select(".c-exhibition-teaser__inner-wrap"):
		title = item.select_one(".c-exhibition-teaser__title-link .text").get_text(strip=True)
		date = item.select_one(".c-exhibition-teaser__date").get_text(strip=True)
		dates = date.split("–")

		# Clean up dates
		dates = [item.strip() for item in dates]
		dates = [" ".join(item.split()) for item in dates]

		exhibits.append(Exhibit(title, dates[0], dates[1]))
		
	return exhibits

def setup_museums() -> list:
	# TODO: Incorporate configuration to denylist some museums for checking
	# I believe American Woman and American Latino exhibits show up under the museum physically hosting them.
	return [Museum("National Air and Space Museum", 1475754763122),
	Museum("National Air and Space Udvar-Hazy Center", 1475754669108),
	Museum("Hirshhorn Art Museum", 1475754534442),
	Museum("Smithsonian Castle", 1475756936235),
	Museum("National Museum of African Art", 1475755005223),
	Museum("Arthur M. Sackler Gallery (Asian Art)", 1475754368943),
	Museum("Freer Gallery of Art (Asian Art)", 1475754256192),
	Museum("African American History and Culture Museum", 1475754916881),
	Museum("Natural History Museum", 1475755442781),
	Museum("American History Museum", 1475755303891),
	Museum("American Art Museum", 1475756550988),
	Museum("National Portrait Gallery", 1475755699216),
	Museum("American Indian Museum (DC)", 1475755580110),
	Museum("Renwick Gallery", 1475756433913),
	Museum("Postal Museum", 1475755828442),
	Museum("National Zoo", 1475756003109),
	Museum("Anacostia Community Museum", 1475753666790),
	Museum("Smithsonian Gardens", 1475756802542)]

def main():
	museums = setup_museums()
	for museum in museums:
		if museum.check:
			try:
				museum.add_future_exhibits(query_museum_upcoming(museum.uuid))
				time.sleep(1)
			except:
				pass #TODO: Add logging for the except case when a museum returns no results
				

if __name__ == "__main__":
    sys.exit(main())

# Current exhibitions URL for ref:
# https://www.si.edu/exhibitions?edan_fq%5B0%5D=p.event.location.extended.location_id%3A%22p1b-1474716020541-1475754763122-0%22