import csv, argparse, logging
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright
from time import sleep

####
####To Run at Command Line:
####python Bulk-Download-Images-from-Shutterstock.py <SHUTTERSTOCK_UID> <SHUTTERSTOCK_PASSWORD> <PATH_TO_INPUT_CSV> <PATH_TO_DOWLOAD_FOLDER>
####
#usage: Sean Creedon's Stock Image Downloader [-h] uid password csv path
#
#Download a stock image from Shutterstock for each term of a given list (CSV).
#
#positional arguments:
#  uid
#  password
#  csv
#  path
#
#options:
#  -h, --help  show this help message and exit


parser = argparse.ArgumentParser(prog="Sean Creedon's Stock Image Downloader", description="Download a stock image from Shutterstock for each term of a given list (CSV).", epilog="Execution Successfull")
#User credentials:
parser.add_argument("uid")
parser.add_argument("password")
#input .CSV:
parser.add_argument("csv")
#output (images, logs . . .):
parser.add_argument("path")
args = parser.parse_args()
uid = args.uid
password = args.password
inputCVS = Path(args.csv)
downloadPath = Path(args.path)

if not downloadPath.exists():
    print("The target directory doesn't exist")
    raise SystemExit(1)
print(f"Shutterstock Usuer ID: {uid}, Shutterstock Password: {password}, Path to Input CSV: {inputCVS} Path to Download Folder: {downloadPath}")

##Logging:
#Create timestamp:
startTime = datetime.now().strftime("%m-%d-%Y-%I-%M-%S%p")

fullLogPath = Path(f"{downloadPath}\logs-{startTime}.txt")
logOfTermsWithoutImages = Path(f"{downloadPath}\Terms_without_Images.txt")
if not logOfTermsWithoutImages.is_file():
	with open(logOfTermsWithoutImages, mode='w', newline='') as missingImageLog:
		missingImageLog.write("Search Terms NOT Found on Shutterstock:\n\n")

def writeLog(content: str):
	"""Writes its content param to the log file. For any custom messages not created by logging library."""
	with open(fullLogPath, mode='a', newline='') as outputTXT:
		outputTXT.write(f"\n{content}\n")
	return None
try:
	with open(fullLogPath, mode='w', newline='') as outputTXT:
		outputTXT.write(f"Logs for Bulk-Download-Images-from-Shutterstock.py run started at {startTime}:\n\n")
except Exception as createLogError:
	writeLog(f"Logs for Bulk-Download-Images-from-Shutterstock.py run started at {startTime}:\n\nWell we're not off to good start.\nCould not write log header due to:\n{createLogError}")
logging.basicConfig(filename=fullLogPath, filemode='a', format='%(name)s - %(levelname)s - %(message)s')

try:
	listOfTerms = []
	with open(inputCVS, "r", encoding="utf8", errors="replace") as readCSV:
		csv_reader = csv.DictReader(readCSV)
		for row in csv_reader:
			newTerm = row["description"]
			listOfTerms.append(newTerm)
			print(f"Added {newTerm} to list of terms to search")
	print(f"Total number of terms to search:\t{len(listOfTerms)}")
	sleep(2)
	for num, second in enumerate(range(3)):
		print(f"Launching in {3 - num}...")
		sleep(1)
except Exception as buildListError:
	#writeLog(f"\n{buildListError}")
	logging.error("Exception occurred", exc_info=True)

#Browswer automation:
#Change invisible to True to "run in background":
invisible = False
base_url = fr"https://accounts.shutterstock.com"
browserUserData = f"{downloadPath}\Playwright_Data"

def waitForNetworkIdle(playwright: Playwright, integer: int)-> None:
	"""Pauses execution for the number of seconds given as integer then checks/waits for an idle network; returns None."""
	#Used to pause web browsing to give more time for pages to load or other events.
	global ShutterstockPage, browser
	sleep(integer)
	ShutterstockPage.wait_for_load_state("networkidle", timeout=0)
	sleep(0.5)
	return None

def openShutterstock(playwright: Playwright) -> None:
	"""Opens a browser, logs into shutterstock.com, then goes to the home page."""
	global ShutterstockPage, browser
	browser = playwright.chromium.launch_persistent_context(browserUserData, args = ["--start-fullscreen" ,"--start-maximized"], base_url = base_url, downloads_path=downloadPath, accept_downloads=True, headless=invisible)
	# Open new page
	ShutterstockPage = browser.new_page()
	#sleep(1)
	# Go to about:base_url
	ShutterstockPage.goto(base_url, timeout=0)
	try:
		# Click [placeholder="Username or Email"]
		ShutterstockPage.click("[placeholder=\"Username or Email\"]", timeout=500)
		# Fill [placeholder="Username or Email"]
		ShutterstockPage.fill("[placeholder=\"Username or Email\"]", uid)
		# Click [placeholder="Password"]
		ShutterstockPage.click("[placeholder=\"Password\"]", timeout=500)
		# Fill [placeholder="Password"]
		ShutterstockPage.fill("[placeholder=\"Password\"]", password)
		# Click button:has-text("Sign in")
		ShutterstockPage.click("button:has-text(\"Sign in\")", timeout=500)
		waitForNetworkIdle(playwright, 1)
	except Exception as authenticationError:
		#writeLog(f"\n{authenticationError}")
		logging.error("Unable to log in. Log-in page may have been skipped or there may have been an error.", exc_info=False)
	ShutterstockPage.goto(fr"https://www.shutterstock.com", timeout=0)
	waitForNetworkIdle(playwright, 1)
	
	return None


def loopDownloadImages(playwright: Playwright, inputList: list) -> None:
	"""Loops through list of strings given as param, searches shutterstock for each string and downloads first result."""
	global ShutterstockPage, browser
	for num, term in enumerate(inputList, 1):
		# Click [placeholder="Search for images"]
		ShutterstockPage.click("[placeholder=\"Search for images\"]", timeout=0)
		sleep(1)
		# Fill [placeholder="Search for images"]
		ShutterstockPage.fill("[placeholder=\"Search for images\"]", term)
		sleep(1)
		# Click [aria-label="Search"]
		# with ShutterstockPage.expect_navigation(url="https://www.shutterstock.com/search/detergent"):
		with ShutterstockPage.expect_navigation():
		    ShutterstockPage.click("[aria-label=\"Search\"]", timeout=0)
		    sleep(1.5)
		try:
			# Click text=Close
			ShutterstockPage.click("text=Close", timeout=2000)
		except Exception as closeAIButtonMissing:
			#print(f"{closeAIButtonMissing}")#Just turning off the AI search tool tip if present.
			pass
		#If no search results:
		if (ShutterstockPage.query_selector("[data-automation=\"NoSearchResultsWithImages_Header\"]")) or (ShutterstockPage.query_selector("[data-automation=\"NoSearchResults_Header_Typography\"]")):
			with open(logOfTermsWithoutImages, mode='a', encoding="utf8", errors="ignore", newline='') as missingImageLog:
				missingImageLog.write(f"{term}\n")
			print(f"No images found for {term}")
			ShutterstockPage.goto(fr"https://www.shutterstock.com")
			waitForNetworkIdle(playwright, 1)
			continue
		# Click text=Image type
		ShutterstockPage.click("text=Image type", timeout=0)
		sleep(1)
		with ShutterstockPage.expect_navigation():
			ShutterstockPage.click("[aria-label=\"Photos\"]", timeout=0)
			sleep(1)
		# Press Escape
		ShutterstockPage.keyboard.press("Escape")
		sleep(1)
		# Click text=More
		ShutterstockPage.click("text=More", timeout=0)
		sleep(1)
		# Click [aria-label="Non editorial"]
		# with ShutterstockPage.expect_navigation(url="https://www.shutterstock.com/search/detergent?release=non-editorial"):
		with ShutterstockPage.expect_navigation():
			ShutterstockPage.click("[aria-label=\"Non editorial\"]", timeout=0)
			sleep(1)
		#If there are no non-editorial search results:
		if ( ShutterstockPage.query_selector("[data-automation=\"NoSearchResultsWithImages_Header\"]") ) or ( ShutterstockPage.query_selector("[data-automation=\"NoSearchResults_Header_Typography\"]") ):
			with open(logOfTermsWithoutImages, mode='a', newline='') as missingImageLog:
				missingImageLog.write(f"{term}\n")
			ShutterstockPage.goto(fr"https://www.shutterstock.com")
			waitForNetworkIdle(playwright, 1)
			continue
		# Press Escape
		ShutterstockPage.keyboard.press("Escape")
		sleep(1)
		ShutterstockPage.locator(".mui-t7xql4-a-inherit-link >> nth=0").click()
		#firstMatch.click()
		#ShutterstockPage.click(".mui-t7xql4-a-inherit-link")
		with ShutterstockPage.expect_download(timeout=0) as download_info:
			ShutterstockPage.click("button:has-text(\"Download\")")
			#print("clicked 1st download button")
			sleep(1)
			try:
				ShutterstockPage.click("button:has-text(\"Download\") >> nth=1")
				#ShutterstockPage.click("[aria-label=\"Download\"]")
				#print("clicked 2nd download button")
			except Exception as alreadyLicensed:
				ShutterstockPage.click("button:has-text(\"Redownload\")")
				#ShutterstockPage.click("[aria-label=\"Redownload\"]")
				#print("clicked redownload button")
			sleep(1)
		downloadFileName = term.replace(" ", "_").replace("(", "").replace(")", "").replace("/", "-")
		download = download_info.value
		download.save_as(f"{downloadPath}\{downloadFileName}.jpg")
		sleep(5)
		writeLog(f"Downloaded file {term}.jpg")
		print(f"Downloaded file {term}.jpg")
		###Script kept dying after about 20 images due to blank "reload chrome" screen. Trying to proactively reload.
		######Maybe query if element exists after clicking 1st download button, or after initial search??
		'''if num % 21 == 0:
			ShutterstockPage.reload(wait_until="networkidle")
			#Just look for a reload button?'''
		'''if ShutterstockPage.query_selector("button:has-text(\"Reload\")"):
			ShutterstockPage.click("button:has-text(\"Reload\")")
			sleep(3)'''
		ShutterstockPage.goto(fr"https://www.shutterstock.com")
		waitForNetworkIdle(playwright, 1)
		sleep(1)
		
	return None

def closeShutterstock(playwright: Playwright) -> None:
	# Close page/browser.
	global ShutterstockPage, browser
	ShutterstockPage.close()
	browser.close()
	return None

def runAllAndDownloadImages(playwright):
	openShutterstock(playwright)
	loopDownloadImages(playwright, listOfTerms)
	closeShutterstock(playwright)
	writeLog("\n\nExecution Successfull")

try:
	with sync_playwright() as playwright:
		runAllAndDownloadImages(playwright)
except Exception as mainFunctionError:
	#writeLog(f"\n{mainFunctionError}")
	writeLog(f"\n###End of Download List###\n\n")#Just add some verticle/blank space between list of downloaded files and fatal error:
	logging.error("Exception occurred:\n", exc_info=True)


###Sample Commands
#Help:
#python E:\Chive_Lab\Bulk-Download-Images-from-Shutterstock.py -h
#Run:
#python E:\Chive_Lab\Bulk-Download-Images-from-Shutterstock.py TestUID TestPassword E:\Chive_Lab