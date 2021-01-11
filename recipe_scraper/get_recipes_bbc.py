import requests
import xml.etree.ElementTree as ET
from os import path
from recipe_scrapers import scrape_me

NUMBER_OF_RECIPES = 100000

tree = ET.parse("sitemap.xml")
root = tree.getroot()

sites = set()

counter = 0
for child in root:
	if counter >= NUMBER_OF_RECIPES:
		break
	url = child[0].text
	if "https://www.bbcgoodfood.com/recipes/" in url:
		sites.add(url)
		counter+=1
with open("data.txt", "w", encoding='utf-8') as data:
	data.write("")

for i, site in enumerate(sites):
	print("Scraping recipe {}/{}".format(i, len(root), end="\r"))
	scraper = scrape_me(site)
	with open("data.txt", "a", encoding='utf-8') as data:
		text = ""
		try:
			text += "{}\n\n".format(scraper.title())
		except AttributeError:
			continue
		try:
			text += "Takes {} minutes\n\n".format(scraper.total_time())
		except AttributeError:
			pass
		text += "Ingredients:\n"
		for ingredient in scraper.ingredients():
			text += "{}\n".format(ingredient)
		text += ("\nMethod:\n")
		for num, item in enumerate(scraper.instructions().split("\n"), 1):
			text += "{}. {}\n".format(num, item)
		text += "\n\n"
		data.write(text)

print(str(len(sites)) + " sites processed") 