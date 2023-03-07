from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
import time
from fuzzywuzzy import fuzz

#What are you looking for at bestbuy?
searchbarinput =input("What would you like to look for today? \n")

# create empty lists to store the Best Buy results
bestbuy_prices = []
bestbuy_prod_names = []

# create a new Chrome browser instance
driver = webdriver.Chrome()

# navigate to the Best Buy page
driver.get("https://www.bestbuy.ca/en-ca")

# find the search bar and enter a search query
search_bar = driver.find_element(By.NAME, "search")
search_bar.send_keys(searchbarinput)
search_bar.send_keys(Keys.RETURN)

# wait for the search results page to load
time.sleep(20)

results = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "medium_1n4Qn", " " ))]//div') 
product_list = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "productItemName_3IZ3c", " " ))]')

for i in range(len(results)):
    bestbuy_prices.append(results[i].text)
    bestbuy_prod_names.append(product_list[i].text)


# save prices and prod_names to a CSV file
df = pd.DataFrame({"Price": bestbuy_prices, "Product Name": bestbuy_prod_names})
df.to_csv(r"bestbuyfiles.csv", index=False)

# close the browser
driver.quit()

# PART 2 HERE
# create a new Chrome browser instance
driver = webdriver.Chrome()

# read in the Best Buy CSV file
df_bestbuy = pd.read_csv("bestbuyfiles.csv")

# create empty lists to store the eBay product names and prices
ebay_prod_names = []
ebay_prices = []

# loop through the rows of df_bestbuy and search for the products on eBay
for index, row in df_bestbuy.iterrows():
    # skip blank rows
    if pd.isnull(row['Product Name']):
        continue
    
    # navigate to eBay and search for the product using the first 20 letters of the product name
    driver.get('https://www.ebay.ca/')
    search_bar = driver.find_element(By.ID, 'gh-ac')
    search_term = ' '.join(row['Product Name'].split()[:5])
    search_bar.send_keys(search_term)
    search_bar.send_keys(Keys.RETURN)
    
    # wait for the search results page to load
    time.sleep(7)
    
    # loop through the search results and find the closest match to the product name
    product_list = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "s-item__title", " " ))]')
    best_match = None
    best_ratio = 0
    for product in product_list:
        ratio = fuzz.partial_ratio(row['Product Name'], product.text)
        if ratio > best_ratio:
            best_match = product
            best_ratio = ratio

    # if a match was found, parse the price and append to the eBay lists
    if best_match is not None and best_ratio >= 70:
        price_element = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "s-item__price", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "ITALIC", " " ))]')
        if price_element:
            price = price_element[0].text
            ebay_prices.append(price)
        else:
            ebay_prices.append("N/A")
        ebay_prod_names.append(best_match.text)
        print("Found match for {} on eBay with price {}".format(best_match.text, price))
    else:
        print("No match found for {} on eBay".format(row['Product Name']))
        ebay_prod_names.append("N/A")
        ebay_prices.append("N/A")



# close the web driver
driver.close()

min_len = min(len(df["Product Name"]), len(bestbuy_prices), len(ebay_prod_names), len(ebay_prices))


# create a new data frame with four columns
df_combine = pd.DataFrame({
    "Product Name": df["Product Name"][:min_len],
    "BestBuy_Price": bestbuy_prices[:min_len],
    "Ebay_Prod": ebay_prod_names[:min_len],
    "Ebay_Price": ebay_prices[:min_len]
})

# save the data frame to a CSV file
df_combine.to_csv("bestbuy_ebay_prices.csv", index=False)
df.to_csv("bestbuy_prices.csv", index=False)
