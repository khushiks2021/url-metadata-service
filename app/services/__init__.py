import httpx
from bs4 import BeautifulSoup
from ..models import URLMetadata

async def fetch_metadata(url: str) -> URLMetadata:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.find('title').text.strip() if soup.find('title') else None

            # Extract Open Graph metadata
            og_title = soup.find('meta', property='og:title')
            if og_title:
                title = og_title.get('content', title)

            description = None
            og_desc = soup.find('meta', property='og:description')
            if og_desc:
                description = og_desc.get('content')
            elif soup.find('meta', attrs={'name': 'description'}):
                description = soup.find('meta', attrs={'name': 'description'}).get('content')

            image = None
            og_image = soup.find('meta', property='og:image')
            if og_image:
                image = og_image.get('content')

            site_name = None
            og_site = soup.find('meta', property='og:site_name')
            if og_site:
                site_name = og_site.get('content')

            return URLMetadata(
                url=url,
                title=title,
                description=description,
                image=image,
                site_name=site_name
            )
        except Exception as e:
            # Return minimal metadata on error
            return URLMetadata(url=url)
