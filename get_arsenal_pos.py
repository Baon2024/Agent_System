import requests
from bs4 import BeautifulSoup

def get_arsenal_position():
    url = 'https://www.bbc.com/sport/football/premier-league/table'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table')
    if not table:
        print('Table not found')
        return

    rows = table.find_all('tr')
    for row in rows:
        if 'Arsenal' in row.text:
            cells = row.find_all('td')
            if cells:
                pos = cells[0].text.strip()
                print(f'Arsenal Position: {pos}')
                return
    print('Arsenal not found in table')

if __name__ == '__main__':
    get_arsenal_position()