from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# ✅ Step 1: Launch Chrome
driver = webdriver.Chrome()
driver.get("https://iprsearch.ipindia.gov.in/PublicSearch/")
driver.maximize_window()
print("🔹 Opening inPASS Patent Search Page...")
time.sleep(5)

try:
    # ✅ Step 2: Select “Title” in dropdown
    select_field = Select(driver.find_element(By.XPATH, "//select[contains(@class,'item-select')]"))
    select_field.select_by_visible_text("Title")
    print("✅ Selected 'Title' from dropdown")

    # ✅ Step 3: Enter the title keyword
    title_text = input("📝 Enter the Title keyword to search: ")
    search_input = driver.find_element(By.XPATH, "//input[@placeholder='e.g. COMPUTER IMPLEMENTED']")
    search_input.send_keys(title_text)
    print(f"✅ Entered title: {title_text}")

    # ✅ Step 4: Handle CAPTCHA (manual)
    captcha_value = input("🧩 Please type the Captcha shown in browser: ")
    captcha_box = driver.find_element(By.XPATH, "//input[@placeholder='Enter Captcha']")
    captcha_box.send_keys(captcha_value)
    print("✅ Captcha entered successfully")

    # ✅ Step 5: Click Search
    search_btn = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Search']")
    search_btn.click()
    print("🔍 Searching...")
    time.sleep(3)

    # ✅ Step 6: Wait for search results
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table//tr")))
    print("🔹 Search results loaded successfully.")

    abstracts = {}
    results = []

    def extract_results():
        """Extracts application numbers, titles, and abstracts from current page"""
        re = []
        rows = driver.find_elements(By.XPATH, "//table//tr")

        for row in rows:
            try:
                button = row.find_element(By.NAME, "ApplicationNumber")
                cells = row.find_elements(By.TAG_NAME, "td")

                if len(cells) >= 2:
                    app_number = button.get_attribute("value").strip()
                    title = cells[1].text.strip()
                    re.append({"application_number": app_number, "title": title, "button": button})
            except:
                continue

        if not re:
            print("❌ No results found on this page.")
            return []

        for i, record in enumerate(re):
            main_window = driver.current_window_handle
            driver.execute_script("arguments[0].click();", record["button"])
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

            new_window = [w for w in driver.window_handles if w != main_window][0]
            driver.switch_to.window(new_window)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//td/strong[contains(text(),'Abstract')]"))
                )
                abstract_element = driver.find_element(By.XPATH, "//td/strong[contains(text(),'Abstract')]/parent::td")
                abstract_text = abstract_element.text.replace("Abstract:", "").strip()
                abstracts[record["application_number"]] = abstract_text
            except:
                abstracts[record["application_number"]] = "Abstract not found."

            driver.close()
            driver.switch_to.window(main_window)

        return re

    # ✅ Step 7: Extract data from first page
    results.extend(extract_results())

    # ✅ Step 8: Try going to the next page (if available)
    try:
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'next')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        print("🔹 Clicked 'Next' button.")
        time.sleep(2)
        results.extend(extract_results())
    except:
        print("ℹ️ No next page found or only one page of results.")

    # ✅ Step 9: Save results to JSON
    serializable_results = [
        {
            "application_number": r["application_number"],
            "title": r["title"],
            "abstract": abstracts.get(r["application_number"], "")
        }
        for r in results
    ]

    output_file = "patent_search_results1.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(serializable_results, f, indent=4, ensure_ascii=False)

    print(f"✅ Extracted and saved {len(results)} records in '{output_file}'")

except Exception as e:
    print("⚠️ Error occurred:", e)

finally:
    driver.quit()
    print("✅ Browser closed.")
