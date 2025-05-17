import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_image_url():
    try:
        # First get the main page
        base_url = "https://www.frontpages.com/the-guardian/"
        res = requests.get(base_url, timeout=10)
        res.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(res.content, "html.parser")
        
        # Look for any image that contains 'the-guardian' in its src
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "the-guardian" in src:
                # Convert relative URL to absolute URL
                return urljoin("https://www.frontpages.com", src)
                
        print("No Guardian image found on the page")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def download_image(url, filename="guardian_frontpage.jpg"):
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        with open(filename, "wb") as f:
            f.write(res.content)
        print(f"Image saved as {filename}")
    except Exception as e:
        print(f"Failed to download image: {e}")

if __name__ == "__main__":
    img_url = get_image_url()
    if img_url:
        print(f"Found image URL: {img_url}")
        download_image(img_url)
    else:
        print("No image URL found.")