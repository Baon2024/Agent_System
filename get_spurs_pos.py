import requests
from bs4 import BeautifulSoup

def get_spurs_position():
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
        if 'Tottenham' in row.text:
            cells = row.find_all('td')
            if cells:
                pos = cells[0].text.strip()
                print(f'Tottenham Hotspur Position: {pos}')
                return
    print('Tottenham not found in table')

if __name__ == '__main__':
    get_spurs_position()