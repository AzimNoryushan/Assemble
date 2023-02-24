import requests
from bs4 import BeautifulSoup
from cssbeautifier import beautify
import os
import argparse
from urllib.parse import urljoin

# Create an argument parser object
parser = argparse.ArgumentParser(
    usage='crawler.py <url> <project_name> <deploy_token> [-h] [--custom-header | --custom-footer | --custom]',
    description='Crawler script',
    formatter_class=argparse.RawDescriptionHelpFormatter
)

# Add two required arguments 'url' and 'project_name'
parser.add_argument('url', help='The URL of the website to crawl')
parser.add_argument('project_name', help='The name of the project')
parser.add_argument('deploy_token', help='Deploy token for authentication')

# Create a mutually exclusive group of arguments
group = parser.add_mutually_exclusive_group()

# Add three options to the group
group.add_argument('--custom-header', action='store_true', help='Allow to input div class name for header only')
group.add_argument('--custom-footer', action='store_true', help='Allow to input div class name for footer only')
group.add_argument('--custom', action='store_true', help='Allow to input div class name for header and footer')

# Parse the arguments
args = parser.parse_args()

url = args.url
project_name = args.project_name
deploy_token = args.deploy_token

# create the project directory
if not os.path.exists(project_name):
    os.makedirs(project_name)

# set the new directory as the current working directory
os.chdir(project_name)

# Initialize npm project
os.system("npm init -y")

os.system("npm config set @assemble:registry https://code.dutysheet.com/api/v4/projects/94/packages/npm/")
os.system("npm config set //code.dutysheet.com/api/v4/projects/94/packages/npm/:_authToken " + deploy_token)
os.system("npm install @assemble/branding-cli")
os.system("npx assemble-branding init")

# Make a request to the webpage
response = requests.get(url)

# Parse the HTML
soup = BeautifulSoup(response.content, "html.parser")

# Extract the header and footer elements
header = soup.find("header")
footer = soup.find("footer")

if args.custom_header:
    print('Using custom header option')
    header_class = input("Enter the class name for header element: ")
    header = soup.find("div", class_=header_class)
elif args.custom_footer:
    print('Using custom footer option')
    footer_class = input("Enter the class name for footer element: ")
    footer = soup.find("div", class_=footer_class)
elif args.custom:
    print('Using custom header and footer option')
    header_class = input("Enter the class name for header element: ")
    footer_class = input("Enter the class name for footer element: ")

    header = soup.find("div", class_=header_class)
    footer = soup.find("div", class_=footer_class)
else:
    if header is None and footer is None:
        print("header and/or footer elements are not present in the page")
        header_class = input("Enter the class name for header element: ")
        footer_class = input("Enter the class name for footer element: ")

        header = soup.find("div", class_=header_class)
        footer = soup.find("div", class_=footer_class)
    else:
        pass

# Extract the class names used in the header and footer elements
header_classes = []
for element in header.select('[class]'):
    header_classes.extend(element['class'])

footer_classes = []
for element in footer.select('[class]'):
    footer_classes.extend(element['class'])

# Check if there is a <style> tag in the HTML
style_tags = soup.find_all("style")
if style_tags:
    css_content = ""
    for style_tag in style_tags:
        css_content += style_tag.get_text()
    
else:
    # Extract the URLs of the CSS files
    css_urls = [link["href"] for link in soup.find_all("link", rel="stylesheet")]

    # Remove the URLs that start with "https"
    css_urls = [url for url in css_urls if not url.startswith("https")]

    # Make requests to retrieve the CSS files
    css_content = []
    for css_url in css_urls:
        css_response = requests.get(url + css_url)
        css_content.append(css_response.text)
    css_content = '\n'.join(css_content)

# Extract class names from css files
css_class_names = []
for css_file in css_content:
    css_class_names += [c.split("{")[0].replace(".", "") for c in css_file.split("}") if "." in c]

used_classes = header_classes + footer_classes

# Remove class names that are not used in header or footer
css_class_names = list(set(css_class_names) & set(used_classes))

# Beautify CSS
formatted_css = beautify(css_content)

# Find all the <img> tags on the page
img_tags = soup.find_all('img')

# Extract the URLs of all the images from the <img> tags
img_urls = [img['src'] for img in img_tags]

# create the assets directory
if not os.path.exists('src/assets'):
    os.makedirs('src/assets')

# Download each image and save it to the assets folder
for img_url in img_urls:
    abs_url = urljoin(url, img_url)
    img_name = img_url.split("/")[-1]
    with open(f"src/assets/{img_name}", "wb") as f:
        f.write(requests.get(abs_url).content)

# Save the header, footer and css files to files
with open("src/header.html", "w", encoding="utf-8") as f:
    f.write(str(header.prettify()))
with open("src/footer.html", "w", encoding="utf-8") as f:
    f.write(str(footer.prettify()))
with open("src/styles/main.scss", "a", encoding="utf-8") as f:
    f.write(str(formatted_css))