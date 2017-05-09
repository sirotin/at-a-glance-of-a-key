from selenium import webdriver
import base64

def load_url_and_read_values(url, driver):
    # Load wanted page
    driver.get(url)

    # Show cookie value as it shown in the webpage
    webpage_value = driver.find_element_by_id("current_cookie").text
    print("Current value (from webpage text): %s" % webpage_value)

    # Get actual cookie and show it's value
    cookie = driver.get_cookie("demo")
    if cookie:
        value = cookie["value"]
        print("Current cookie value is: %s (decoded: %s)" % (value, base64.b64decode(value)))
    else:
        print("Cookie does not exist!")

if __name__ == "__main__":
    # Start chrome web browser
    url = "http://localhost:55438/Default.aspx"
    driver = webdriver.Chrome()

    # Check current page values
    print("==== Demo 1: Read initial web-site values ====")
    load_url_and_read_values(url, driver)

    # Update the cookie using the web-page form
    print("==== Demo 2: Automate web-page form filling ====")
    driver.find_element_by_id("cookie_value").send_keys("form submit")
    driver.find_element_by_id("form_submit").click()

    # Check current page values
    load_url_and_read_values(url, driver)

    # Update the cookie
    print("==== Demo 3: Update cookie ====")
    cookie = driver.get_cookie("demo")
    if cookie:
        cookie["value"] = base64.b64encode("set cookie")
    else:
        cookie = { "domain" : "localhost",
                   "expiry" : None,
                   "httpOnly" : False,
                   "name" : "demo",
                   "path" : "/",
                   "secure" : False,
                   "value" : base64.b64encode("set cookie") }
    driver.delete_cookie("demo")
    driver.add_cookie(cookie)

    # Check current page values
    load_url_and_read_values(url, driver)

    # Close the web browser
    driver.quit()