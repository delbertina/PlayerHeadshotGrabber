from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import urllib.request
import time
from PIL import Image, ImageOps
from tkinter.filedialog import askopenfilename


def pose_character():
    # Somewhat arbitrary numbers for rotation sliders
    rotate_x = -6
    rotate_y = 15
    # Click the pose tab
    nav_pose_button = driver.find_element_by_css_selector("#pose")
    nav_pose_button.click()
    # Mode X Slider
    rotation_slider_x_node = driver.find_element_by_css_selector("div.slider:nth-of-type(1) > a")
    ActionChains(driver).click_and_hold(rotation_slider_x_node) \
        .move_to_element_with_offset(rotation_slider_x_node, rotate_x, 0) \
        .release().perform()
    # Move Y Slider
    rotation_slider_y_node = driver.find_element_by_css_selector("div.slider:nth-of-type(2) > a")
    ActionChains(driver).click_and_hold(rotation_slider_y_node) \
        .move_to_element_with_offset(rotation_slider_y_node, rotate_y, 0) \
        .release().perform()
    driver.find_element_by_css_selector("#gallery").click()


def prepare_render(input_username):
    # Enter the username into the search box
    skin_search_box = driver.find_element_by_id("gallery-search")
    skin_search_box.send_keys(Keys.CONTROL, "a")
    skin_search_box.send_keys(Keys.DELETE)
    skin_search_box.send_keys("@" + input_username)
    skin_search_box.send_keys(Keys.RETURN)
    # Wait until the search result return
    wait = WebDriverWait(driver, 10)
    wait.until(expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "partdetail")))
    # Click the load skin button
    skin_load_button = driver.find_element_by_css_selector("div.partzoom.base > button.load")
    skin_load_button.click()
    # The website has a race condition, just give 'er a second ... literally
    time.sleep(1)
    # Click picture button
    driver.find_element_by_css_selector("#screenshot").click()
    # Get image src
    wait.until(expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "fancybox-image")))
    return_value = driver.find_element_by_css_selector("img.fancybox-image").get_attribute("src")
    # Reset to gallery tab
    wait.until(expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "fancybox-close")))
    driver.find_element_by_css_selector("div.fancybox-close").click()
    wait.until(expected_conditions.invisibility_of_element_located((By.ID, "fancybox-overlay")))
    driver.find_element_by_css_selector("#gallery").click()
    return return_value


def save_with_backgrounds(input_username, input_image, image_size):
    # Colors
    background_blue = "#264653"
    background_green = "#2A9D8F"
    background_yellow = "#E9C46A"
    background_orange = "#F4A261"
    background_red = "#E76F51"
    # Images of colors
    background_image_blue = Image.new("RGB", (image_size, image_size), background_blue)
    background_image_green = Image.new("RGB", (image_size, image_size), background_green)
    background_image_yellow = Image.new("RGB", (image_size, image_size), background_yellow)
    background_image_orange = Image.new("RGB", (image_size, image_size), background_orange)
    background_image_red = Image.new("RGB", (image_size, image_size), background_red)
    # Paste input image onto the images of colors and save
    background_image_blue.paste(input_image, (0, 0), input_image)
    background_image_blue.save('image-output/skin-' + input_username + '-blue.png')
    background_image_green.paste(input_image, (0, 0), input_image)
    background_image_green.save('image-output/skin-' + input_username + '-green.png')
    background_image_yellow.paste(input_image, (0, 0), input_image)
    background_image_yellow.save('image-output/skin-' + input_username + '-yellow.png')
    background_image_orange.paste(input_image, (0, 0), input_image)
    background_image_orange.save('image-output/skin-' + input_username + '-orange.png')
    background_image_red.paste(input_image, (0, 0), input_image)
    background_image_red.save('image-output/skin-' + input_username + '-red.png')


# Get list of usernames
username_list = []
temp_name_file = askopenfilename()
for line in open(temp_name_file):
    username_list.append(line.strip())
# Load the website
driver = webdriver.Firefox()
driver.get("https://minecraft.novaskin.me/")
assert "Nova Skin" in driver.title
pose_character()
# For each username in the list
for username in username_list:
    # Get image src from page
    imageSrc = prepare_render(username)
    # Save image from src
    response = urllib.request.urlopen(imageSrc)
    with open('novaskin-download/skin-' + username + '.png', 'wb') as f:
        f.write(response.file.read())
    # Make image with transparency
    transparent_head = ImageOps.expand(
        ImageOps.fit(
            ImageOps.expand(
                Image.open('novaskin-download/skin-' + username + '.png'),
                border=10, fill=(255, 255, 255, 0)), size=(210, 210), centering=(0, 0)
        ), border=5, fill="black")
    # Save image with different backgrounds
    save_with_backgrounds(username, transparent_head, 220)
print('Done')
