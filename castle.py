from playwright.sync_api import sync_playwright
from playwright_stealth.stealth import Stealth
from bs4 import BeautifulSoup
import argparse
from datetime import datetime, date, timedelta
import sys
import time
import json
import os
	
class Museum:
	def __init__(self, name, uuid, check=True):
		self.name = name
		self.uuid = uuid
		self.check = check
		self.current_exhibits = []
		self.future_exhibits = []
		
	def add_current_exhibits(self, exhibits):
		self.current_exhibits.extend(exhibits)
		
	def add_future_exhibits(self, exhibits):
		self.future_exhibits.extend(exhibits)
		
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
		datetime.strptime(date_str, "%B %d, %Y")
		return True
	except ValueError:
		return False

def query_museum_exhibits(museum_uuid, future: bool) -> list: #TODO: Convert to general queryer with option for upcoming or not 
	with Stealth().use_sync(sync_playwright()) as p:
		browser = p.chromium.launch()
		page = browser.new_page()
		
		upcoming = "/upcoming" if future else ""
		page.goto(f'https://www.si.edu/exhibitions{upcoming}?edan_fq[0]=p.event.location.extended.location_id:"p1b-1474716020541-{museum_uuid}-0"')
		page.locator(".c-exhibition-teaser__inner-wrap").first.wait_for(timeout=15000)
		soup = BeautifulSoup(page.content(), "html.parser")
		browser.close()
		
	exhibits = []

	for item in soup.select(".c-exhibition-teaser__inner-wrap"):
		title = item.select_one(".c-exhibition-teaser__title-link .text").get_text(strip=True)
		date = item.select_one(".c-exhibition-teaser__date").get_text(strip=True)
		dates = date.split("–") if "–" in date else date.split("Through")

		# Clean up dates
		dates = [item.strip() for item in dates]
		dates = [" ".join(item.split()) for item in dates]
		
		from_date = datetime.strptime(dates[0], "%B %d, %Y") if is_valid_date(dates[0]) else dates[0]
		to_date = datetime.strptime(dates[1], "%B %d, %Y") if is_valid_date(dates[1]) else dates[1]

		exhibits.append(Exhibit(title, from_date, to_date))
		
	return exhibits

def setup_museums() -> list:
	# TODO: Incorporate configuration to denylist some museums for checking
	# I believe American Woman and American Latino exhibits show up under the museum physically hosting them.
	return [Museum("National Air and Space Museum", 1475754763122),
# 	Museum("National Air and Space Udvar-Hazy Center", 1475754669108),
# 	Museum("Hirshhorn Art Museum", 1475754534442),
# 	Museum("Smithsonian Castle", 1475756936235),
# 	Museum("National Museum of African Art", 1475755005223),
# 	Museum("Arthur M. Sackler Gallery (Asian Art)", 1475754368943),
# 	Museum("Freer Gallery of Art (Asian Art)", 1475754256192),
# 	Museum("African American History and Culture Museum", 1475754916881),
# 	Museum("Natural History Museum", 1475755442781),
# 	Museum("American History Museum", 1475755303891),
# 	Museum("American Art Museum", 1475756550988),
# 	Museum("National Portrait Gallery", 1475755699216),
# 	Museum("American Indian Museum (DC)", 1475755580110),
# 	Museum("Renwick Gallery", 1475756433913),
# 	Museum("Postal Museum", 1475755828442),
# 	Museum("National Zoo", 1475756003109),
# 	Museum("Anacostia Community Museum", 1475753666790),
	Museum("Smithsonian Gardens", 1475756802542)]
	
UPCOMING_CACHE = os.path.expanduser("~/.local/share/castle/upcoming.json")

def upcoming(museums: list):
	for museum in museums:
		if museum.check:
			try:
				museum.add_future_exhibits(query_museum_exhibits(museum.uuid, True))
				time.sleep(1)
			except Exception as e:
				print(f"  {museum.name}: {e}")

	
	# Load previously known exhibits
	known = {}
	if os.path.exists(UPCOMING_CACHE):
		with open(UPCOMING_CACHE) as f:
			known = json.load(f)
			
	# Alert on new exhibits
	for museum in museums:
		new = [e for e in museum.future_exhibits if e.name not in known.get(museum.name, [])] if museum.future_exhibits else []
		if new:
			print(museum.name)
			for e in new:
				from_str = e.from_date.strftime("%B %d, %Y") if isinstance(e.from_date, datetime) else e.from_date
				to_str = e.to_date.strftime("%B %d, %Y") if isinstance(e.to_date, datetime) else e.to_date
				print(f"  {e.name} ({from_str} - {to_str})")

	# Update cache: only overwrite values for museums checked this run
	os.makedirs(os.path.dirname(UPCOMING_CACHE), exist_ok=True)
	known.update({m.name: [e.name for e in m.future_exhibits] for m in museums if m.future_exhibits})
	with open(UPCOMING_CACHE, "w") as f:
		json.dump(known, f, indent=2)
				
def is_within_period(target_date, days):
	today = datetime.now()
	return today <= target_date <= today + timedelta(days=days)

def this_week(museums: list, days):
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
				if isinstance(exhibit.from_date, datetime) and is_within_period(exhibit.from_date, days):
					print(f"{exhibit.name} starts on{exhibit.from_date: %B %d, %Y}")
	
	print("CLOSING THIS WEEK")
	for museum in museums:
		if museum.check:
			print(f"{museum}:")
			for exhibit in museum.current_exhibits:
				if isinstance(exhibit.to_date, datetime) and is_within_period(exhibit.to_date, days):
					print(f"{exhibit.name} closes on{exhibit.to_date: %B %d, %UY}")


def main():
	# General setup.
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(title='SUBCOMMANDS', required=True)
	
	parser_week = subparsers.add_parser('soon', help="Exhibits opening or closing in the next specified (default: 7) days")
	parser_week.add_argument('-d', '--days', help="Number of days to look forward for opening/closing exhibits", default=7, type=int)
	parser_week.set_defaults(func=this_week, subcommand='soon')

	parser_upcoming = subparsers.add_parser('upcoming', help="Prints only upcoming exhibits that have been announced since its last invocation. Note, will print all upcoming on first invocation.")
	parser_upcoming.set_defaults(func=upcoming, subcommand='upcoming')

	args = parser.parse_args()

	museums = setup_museums()

	if args.subcommand == 'soon':
		args.func(museums, args.days)
	else:
		args.func(museums)

if __name__ == "__main__":
	sys.exit(main())
