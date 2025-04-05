from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json

# ✅ Set up Chrome options
chrome_options = Options()
chrome_options.headless = False  # Ensure the browser is visible
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# ✅ Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# ✅ URL of the main page
main_url = "https://iprsearch.ipindia.gov.in/PublicSearch/"

try:
    print("🔹 Opening main page...")
    driver.get(main_url)

    # ✅ Wait for page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)  # Allow JavaScript to load content

    # ✅ Step 2: Search for a Specific Title
    search_title = input("Enter a title to search: ").strip()

    # Find and interact with the search box
    search_box = driver.find_element(By.ID, "TextField1")
    search_box.clear()
    search_box.send_keys(search_title)

    # Click the search button
    search_button = driver.find_element(By.NAME, "submit")
    search_button.click()

    # ✅ CAPTCHA Handling (Manual Entry)
    try:
        captcha_img = driver.find_element(By.ID, "Captcha")
        captcha_url = captcha_img.get_attribute("src")
        print(f"🔹 CAPTCHA detected. Open this URL and solve it manually: {captcha_url}")
        captcha_text = input("Enter the CAPTCHA text: ").strip()

        captcha_input = driver.find_element(By.ID, "CaptchaText")
        captcha_input.send_keys(captcha_text)

        submit_button = driver.find_element(By.NAME, "submit")
        submit_button.click()
        time.sleep(3)

        if "Incorrect CAPTCHA" in driver.page_source:
            print("❌ CAPTCHA verification failed! Try again.")
            driver.quit()
            exit()
        else:
            print("✅ CAPTCHA verified successfully!")

    except Exception:
        print("No CAPTCHA found.")

    # ✅ Wait for search results to load
    results = []

    abstracts = {}
    def yy():
        print("🔹 Waiting for search results...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tr"))
        )
        time.sleep(3)
        re=[]
        # ✅ Extract application numbers and titles using Selenium

        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            try:
                button = row.find_element(By.NAME, "ApplicationNumber")  # ✅ Selenium WebElement
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) >= 2:
                    app_number = button.get_attribute("value").strip()
                    title = cells[1].text.strip()

                    re.append({"application_number": app_number, "title": title, "button": button})

            except:
                continue  # Skip if button not found

        if not re:
            print("❌ No results found. Exiting...")
            driver.quit()
            exit()



        # ✅ Loop through all results on the first page to extract their abstracts
        for selected_index in range(len(re)):
            selected_button = re[selected_index]["button"]

            # ✅ Store the current window handle
            main_window = driver.current_window_handle
            print(f"🔹 Main Window Handle: {main_window}")

            # ✅ Click the button to open the application in a new tab
            driver.execute_script("arguments[0].click();", selected_button)
            print(f"✅ Button for application {re[selected_index]['application_number']} clicked!")

            # ✅ Wait for a new tab to open
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

            # ✅ Switch to new tab
            new_window = [window for window in driver.window_handles if window != main_window][0]
            driver.switch_to.window(new_window)

            # ✅ Wait for the Abstract section to appear
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//td/strong[contains(text(),'Abstract')]"))
                )
                print("✅ Abstract section found!")
            except:
                print("❌ Abstract section not found!")
                driver.close()
                driver.switch_to.window(main_window)
                continue

            # ✅ Extract abstract from the new page
            abstract_element = driver.find_element(By.XPATH, "//td/strong[contains(text(),'Abstract')]/parent::td")
            abstract_text = abstract_element.text.replace("Abstract:", "").strip()

            if abstract_element:
                abstracts[re[selected_index]['application_number']] = abstract_text
            else:
                print(f"❌ Abstract not found for {re[selected_index]['application_number']}.")

            # Close the current tab and switch back to the main window
            driver.close()
            driver.switch_to.window(main_window)
        results.extend(re)





    yy()
    try:
        # ✅ Find and click the "Next" button using <button> tag and class
        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'next')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        print("🔹 Clicked on 'Next' button. Waiting for results to load...")

        # ✅ Wait for the new page content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//table//tr"))
        )
        time.sleep(2)
    except Exception as e:
        print(f"❌ Could not go to next page or retrieve title: {e}")
    yy()

    serializable_results = [
        {
            "application_number": item["application_number"],
            "title": item["title"],
            "abstract":abstracts[item["application_number"]]
        }
        for item in results
    ]
    output_file = "patent_search_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_results, f, indent=4, ensure_ascii=False)

    print(f"✅ Stored {len(results)} records in '{output_file}'")



    # ✅ User selects an application



finally:
    driver.quit()