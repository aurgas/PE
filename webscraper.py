from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# ✅ Setup Chrome WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
#options.add_argument("--headless")  # Run without GUI
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection

# ✅ Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 10)

# ✅ Google Maps search for the restaurant
place_name = "Kanha Restaurant"
search_url = f"https://www.google.com/maps/search/{place_name.replace(' ', '+')}"
driver.get(search_url)
time.sleep(5)

# ✅ Click on the first result
# ✅ Click on the second result instead of the first
try:
    search_results = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.hfpxzc")))
    search_results[0].click()  # Fallback to first if there's no second result
    time.sleep(5)
except Exception as e:
    print(f"❌ Could not find the place. Error: {e}")
    driver.quit()
    exit()

# ✅ Click the "Reviews" button
try:
    reviews_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'reviews')]")))
    reviews_button.click()
    time.sleep(5)
except Exception as e:
    print(f"❌ Reviews button not found. Error: {e}")
    driver.quit()
    exit()

# ✅ Scroll & Click "More Reviews"
try:
    scrollable_div = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf"))
    )

    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
    scroll_attempts = 0

    while scroll_attempts < 2000:  # Increase attempts for better coverage
        # ✅ Instead of scrolling to full height, scroll by a **smaller amount**
        driver.execute_script("arguments[0].scrollTop += 500;", scrollable_div)  # ⬆️ Shorter scroll
        time.sleep(random.uniform(3, 5))  # ⏳ Slow delay

        # ✅ Click "More Reviews" if present
        try:
            more_reviews_buttons = driver.find_elements(By.CSS_SELECTOR, "button.w8nwRe")
            if more_reviews_buttons:
                for button in more_reviews_buttons:
                    driver.execute_script("arguments[0].scrollIntoView();", button)
                    time.sleep(random.uniform(2, 3))  # ⏳ Small delay before clicking
                    driver.execute_script("arguments[0].click();", button)
                    time.sleep(random.uniform(4, 6))  # ⏳ Wait longer for new reviews
                print(f"✅ Clicked 'More Reviews' button {len(more_reviews_buttons)} times.")
        except Exception as e:
            print("⚠️ No 'More Reviews' button found.")

        # ✅ Stop if no new reviews load
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == last_height:
            print("❌ No more new reviews loading. Stopping scroll.")
            break
        last_height = new_height
        scroll_attempts += 1

except Exception as e:
    print(f"❌ Error while scrolling: {e}")
    driver.quit()
    exit()


# ✅ Extract Reviews, Names & Ratings
reviews_data = []
try:
    review_elements = driver.find_elements(By.CSS_SELECTOR, "div.jftiEf")

    for review in review_elements:
        try:
            # ✅ Extract Reviewer Name
            name = review.find_element(By.CSS_SELECTOR, "div.d4r55").text

            # ✅ Extract Review Rating
            rating = review.find_element(By.CSS_SELECTOR, "span.kvMYJc").get_attribute("aria-label")
            rating = rating.split()[0]  # Extract only the number

            # ✅ Expand "Read more" if available
            try:
                more_button = review.find_element(By.CSS_SELECTOR, "button.w8nwRe")
                more_button.click()
                time.sleep(1)
            except:
                pass  # No "Read more" button

            # ✅ Extract Full Review Text
            text = review.find_element(By.CSS_SELECTOR, "span.wiI7pd").text

            reviews_data.append([name, rating, text])

        except Exception as e:
            print(f"❌ Error extracting a review: {e}")

    # ✅ Save to CSV
    df = pd.DataFrame(reviews_data, columns=["Name", "Rating", "Review"])
    df.to_csv("reviews.csv", index=False, encoding="utf-8")

    print(f"✅ Scraped {len(reviews_data)} reviews successfully! Saved as 'reviews.csv'.")

except Exception as e:
    print(f"❌ Error extracting reviews: {e}")

# ✅ Quit WebDriver
driver.quit()
