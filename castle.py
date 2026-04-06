from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth
from bs4 import BeautifulSoup
import argparse
from datetime import datetime
import sys
import time
	
class Museum:
	def __init__(self, name, uuid, check=True):
		self.name = name
		self.uuid = uuid
		self.check = check
		self.current_exhibits = []
		self.future_exhibits = []
		
	def add_current_exhibits(self, exhibits):
		self.current_exhibits.append(exhibits)
		
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
	
def is_valid_date(date_str: str) -> bool:
	try:
		datetime.strptime(date_str, "%m %d, %Y")
		return True
	except ValueError:
		return False

def query_museum_exhibits(museum_uuid, future: bool) -> list: #TODO: Convert to general queryer with option for upcoming or not 
	with Stealth().use_sync(sync_playwright()) as p:
		browser = p.chromium.launch()
		page = browser.new_page()
		
		upcoming = "/upcoming" if future else ""
		page.goto(f'https://www.si.edu/exhibitions{upcoming}?edan_fq[0]=p.event.location.extended.location_id:"p1b-1474716020541-{museum_uuid}-0"')
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
		
		to_date = datetime.strptime(dates[1], "%m %d, %Y") if is_valid_date(dates[1]) else dates[1]

		exhibits.append(Exhibit(title, datetime.strptime(dates[0], "%m %d, %Y"), to_date)) #TODO: Account for "Permanent" and "Indefinitely"
		
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
	
def upcoming(museums: list):
	for museum in museums:
		if museum.check:
			try:
				museum.add_future_exhibits(query_museum_exhibits(museum.uuid, True))
				time.sleep(1)
			except:
				pass #TODO: Add logging for the except case when a museum returns no results
				
	# Compare to stored values.
				
def is_within_period(target_date):
	today = date.today()
	future_limit = today + timedelta(days=7)
	
	# Returns True if the date is today or up to 7 days in the future
	return today <= target_date <= future_limit

def this_week(museums: list):
	for museum in museums:
		if museum.check:
			try:
				museum.add_future_exhibits(query_museum_exhibits(museum.uuid, True))
				museum.add_current_exhibits(query_museum_exhibits(museum.uuid, False))
				time.sleep(1)
			except:
				pass #TODO: Add logging for the except case when a museum returns no results
				
	print("OPENING THIS WEEK")
	
	for museum in museums:
		if museum.check:
			print(f"{museum}:")
			for exhibit in museum.future_exhibits:
				if is_within_period(exhibit.from_date):
					print(f"{exhibit.name} starts on {exhibit.from_date}")
	
	print("CLOSING THIS WEEK")
	for museum in museums:
		if museum.check:
			print(f"{museum}:")
			for exhibit in museum.future_exhibits:
				if exhibit.to_date == "Indefinitely" or exhibit.to_date == "Permanent":
					pass
				if is_within_period(exhibit.to_date):
					print(f"{exhibit.name} closes on {exhibit.to_date}")


def main():
	# General setup.
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(title='SUBCOMMANDS', required=True)
	
	parser_week = subparsers.add_parser('week', help="Exhibits opening or closing in the next 7 days")
	parser_week.set_defaults(func=this_week)

	parser_upcoming = subparsers.add_parser('upcoming', help="Newly announced upcoming exhibits")
	parser_upcoming.set_defaults(func=upcoming)

	args = parser.parse_args()

	museums = setup_museums()

	args.func(museums)	

if __name__ == "__main__":
	sys.exit(main())
