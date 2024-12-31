import requests
import json
from typing import List, Dict, Optional
import time
import validators
from tqdm import tqdm


class ScryfallPriceScraper:
    BASE_URL = "https://api.scryfall.com"


    @staticmethod
    def _get_card_prices_fast(scryfall_uri : str):
        response = requests.get(scryfall_uri)

        if response.status_code == 200:
            data = response.json()
            return ScryfallPriceScraper._extract_card_prices([data])

        return []


    @staticmethod
    def get_card_prices(card:Dict) -> List[Dict]:
        """
        Retrieve price data for MTG cards matching the given criteria.
        
        Args:
            card (str): Dictionary containing all the info for the given card
        
        Returns:
            List of dictionaries containing price information for matching cards
        """
        # Construct the search query
        if "uri" in card and validators.url(card['uri']):
            data = ScryfallPriceScraper._get_card_prices_fast(card['uri'])
            if len(data) > 0:
                return data


        # we dont have a valid uri. perform a full search

        card_name = card['card_name']
        set_code = card['expansion']
        collector_number = card['collector_number']

        query = f'"{card_name}"'
        if set_code:
            query += f' set:{set_code}'
        if collector_number:
            query += f' cn:{collector_number}'

        query += f" game:paper"
        
        # Encode the query for URL
        params = {
            'q': query,
            'unique': 'prints'  # Get all printings of the card
        }
        
        try:
            # Make the search request
            search_response = requests.get(f"{ScryfallPriceScraper.BASE_URL}/cards/search", params=params)
            search_response.raise_for_status()
            
            return ScryfallPriceScraper._build_data(search_response)
        
        except requests.RequestException as e:
            print(f"Error retrieving card data: {e}")
            return []
    
    @staticmethod
    def _extract_card_prices(cards: List[Dict]) -> List[Dict]:
        """
        Extract price information from card data.
        
        Args:
            cards (List[Dict]): List of card data from Scryfall
        
        Returns:
            List of dictionaries with price information
        """
        card_prices = []
        
        for card in cards:
            # Prepare price information dictionary
            price_info = {
                'name': card.get('name', 'Unknown'),
                'set': card.get('set', 'Unknown'),
                'set_name': card.get('set_name', 'Unknown'),
                'prices': {
                    'usd': card.get('prices', {}).get('usd', 'N/A'),
                    'usd_foil': card.get('prices', {}).get('usd_foil', 'N/A'),
                    'eur': card.get('prices', {}).get('eur', 'N/A'),
                    'eur_foil': card.get('prices', {}).get('eur_foil', 'N/A'),
                    'tix': card.get('prices', {}).get('tix', 'N/A'),
                },
                'rarity': card.get('rarity', 'Unknown'),
                'collector_number': card.get('collector_number', 'N/A'),
                'uri': card.get('uri', 'Unknown')
            }
            
            card_prices.append(price_info)
        
        return card_prices
    

    @staticmethod
    def _build_data(search_response : requests.models.Response):
        # Parse the search results
        search_data = search_response.json()
        
        if search_data['total_cards'] > 100:
            raise requests.RequestException("Got more than 100 results. Try be more specific.")

        
        # Collect price information for each card
        card_prices = []
        
        # Process the initial page of results
        card_prices.extend(ScryfallPriceScraper._extract_card_prices(search_data['data']))
        
        # Handle potential pagination
        while search_data.get('has_more', False):
            next_page_url = search_data.get('next_page')
            if not next_page_url:
                break
            
            next_page_response = requests.get(next_page_url)
            next_page_response.raise_for_status()
            search_data = next_page_response.json()
            
            card_prices.extend(ScryfallPriceScraper._extract_card_prices(search_data['data']))
        

        return card_prices
    

def test_get_card():
    # Example usage
    card_name = input("Enter card name: ")
    set_code = input("Enter set code (optional, press Enter to skip): ").strip() or None
    collector_number = input("Enter collector number (optional, press Enter to skip): ").strip() or None
    
    # Retrieve and display card prices
    prices = ScryfallPriceScraper.get_card_prices(card_name, set_code, collector_number)
    
    if not prices:
        print("No cards found.")
        return
    
    # Pretty print the results
    print(f"\nFound {len(prices)} card variations:")
    for card in prices:
        print("\n--- Card Details ---")
        print(f"Name: {card['name']}")
        print(f"Set: {card['set_name']} ({card['set']})")
        print(f"Collector Number: {card['collector_number']}")
        print(f"Rarity: {card['rarity']}")
        print("Prices:")
        print(f"  USD: ${card['prices']['usd']}")
        print(f"  USD Foil: ${card['prices']['usd_foil']}")
        print(f"  EUR: \u20AC{card['prices']['eur']}")
        print(f"  EUR Foil: \u20AC{card['prices']['eur_foil']}")

def load_card_list():
    path = f"./data/cards_list.txt"
    f = open(path)
    lines = f.readlines()
    
    cards = []

    for line in lines:
        if(len(line) == 0 or line[0]=='#'):
            continue

        data = [part.strip() for part in line.split('|')]
        cards.append({
            'card_name': data[0], 
            'expansion': data[1], 
            'collector_number': data[2], 
            'price_usd': data[3],
            'price_usd_foil': data[4],
            'price_eur': data[5],
            'price_eur_foil': data[6],
            'tix': data[7],
            'date': data[8],
            'uri': data[9],
            })

    return cards


def update_cards_data(cards : List, sleep_time:float = 0.06):
    if sleep_time <= 0:
        sleep_time = 0.06
    
    data = []
    for card in tqdm(cards, desc="Updating cards", unit="card", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}] - {postfix}"):
        tqdm.write(f"Updating card: {card['card_name']}...")
        #print(f"Updating card: {card['card_name']}...")
        prices = ScryfallPriceScraper.get_card_prices(card)

        # update price data
        for price in prices:
            data.append({
                'name': price['name'],
                'set_code': price['set'],
                'collector_number': price['collector_number'],
                'price_eur': price['prices']['eur'],
                'price_usd': price['prices']['usd'],
                'price_eur_foil': price['prices']['eur_foil'],
                'price_usd_foil': price['prices']['usd_foil'],
                'uri': price['uri']
            })

        time.sleep(sleep_time)  # sleep for 60 ms
    return data

if __name__ == "__main__":
    test_get_card()
