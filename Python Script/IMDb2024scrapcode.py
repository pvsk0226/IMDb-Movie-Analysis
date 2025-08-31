from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd

# Launch Chrome browser
driver = webdriver.Chrome()

# List of genres to scrape
genres = ["Sport"]

def click_load_more():
    """Click any '... more' button until no more found."""
    try:
        load_more_button = driver.find_element(By.XPATH, "//button//span[contains(text(),'more')]")
        ActionChains(driver).move_to_element(load_more_button).perform()
        load_more_button.click()
        time.sleep(3)
        return True
    except:
        return False

for genre in genres:
    print(f"Scraping {genre.title()} movies...")

    # Open IMDb search page for the genre
    url = f"https://www.imdb.com/search/title/?title_type=feature&release_date=2024-01-01,2024-12-31&genres={genre}"
    driver.get(url)
    time.sleep(3)

    # Keep clicking until no button is found
    while click_load_more():
        print(f"Clicked 'Load More' for {genre.title()}")

    print(f"All {genre.title()} movies loaded")

    # Scrape movie details
    movies_data = []
    movies = driver.find_elements(By.XPATH, "//li[@class='ipc-metadata-list-summary-item']")

    for movie in movies:
        try:
            # Movie Name
            title = movie.find_element(By.XPATH, ".//h3").text

            # Rating
            try:
                rating = movie.find_element(By.XPATH, ".//span[@class='ipc-rating-star--rating']").text
            except:
                rating = "N/A"

            # Votes
            try:
               votes_raw = movie.find_element(By.XPATH, ".//span[@class='ipc-rating-star--voteCount']").text
               votes_raw = votes_raw.replace("(", "").replace(")", "").replace(",", "").replace("–", "").strip()

             # Handle K (thousands) and M (millions)
               if "K" in votes_raw:
                 votes = str(int(float(votes_raw.replace("K", "")) * 1000))
               elif "M" in votes_raw:
                 votes = str(int(float(votes_raw.replace("M", "")) * 1000000))
               elif votes_raw.isdigit():
                   votes = votes_raw
               else:
                  votes = "N/A"
            except:
               votes = "N/A"

            # Duration (only pick values with h or m)
            try:
                metadata_items = movie.find_elements(By.XPATH, ".//span[contains(@class,'dli-title-metadata-item')]")
                duration = next((m.text for m in metadata_items if "h" in m.text or "m" in m.text), "N/A")
            except:
                duration = "N/A"

            # ✅ Hardcode genre from loop
            movies_data.append({
                "Movie Name": title,
                "Genre": genre.title(),
                "Rating": rating,
                "Voting Counts": votes,
                "Duration": duration
            })

        except Exception as e:
            print("Error extracting movie:", e)

    # Save results for this genre into a CSV file
    df = pd.DataFrame(movies_data)
    filename = f"IMDb_2024_{genre.title()}.csv"
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"Data saved to {filename}\n")

driver.quit()
