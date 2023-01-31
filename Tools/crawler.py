import requests
from bs4 import BeautifulSoup
from cssbeautifier import beautify
import sys
import os

url = sys.argv[1] #"https://www.parkinsons.org.uk/"
project_name = sys.argv[2]

# create the directory
if not os.path.exists(project_name):
    os.makedirs(project_name)

# set the new directory as the current working directory
os.chdir(project_name)

# Initialize npm project
os.system("npm init -y")

# Make a request to the webpage
response = requests.get(url)

# Parse the HTML
soup = BeautifulSoup(response.content, "html.parser")

# Extract the header and footer elements
header = soup.find("header")
footer = soup.find("footer")

# Extract the class names used in the header and footer elements
header_classes = [c for c in header.find_all(class_=True) if header.get("class")]
footer_classes = [c for c in footer.find_all(class_=True) if footer.get("class")]

# Extract the URLs of the CSS files
css_urls = [link["href"] for link in soup.find_all("link", rel="stylesheet")]

# Remove the URLs that start with "https"
css_urls = [url for url in css_urls if not url.startswith("https")]

# Make requests to retrieve the CSS files
css_content = []
for css_url in css_urls:
    css_response = requests.get(url + css_url)
    css_content.append(css_response.text)

# Extract class names from css files
css_class_names = []
for css_file in css_content:
    css_class_names += [c.split("{")[0].replace(".", "") for c in css_file.split("}") if "." in c]

# Remove class names that are not used in header or footer
css_class_names = list(set(css_class_names) & set(header_classes + footer_classes))

# Beautify CSS
css_content = '\n'.join(css_content)
formatted_css = beautify(css_content)

# Save the header, footer and css files to files
with open("header.html", "w", encoding="utf-8") as f:
    f.write(str(header.prettify()))
with open("footer.html", "w", encoding="utf-8") as f:
    f.write(str(footer.prettify()))
with open("style.css", "w", encoding="utf-8") as f:
    f.write(str(formatted_css))
