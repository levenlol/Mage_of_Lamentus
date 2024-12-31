import sys, os
ROOT_DIR = os.path.join(os.getcwd(), 'src')

sys.path.append(ROOT_DIR)
import mtg_scraper_scryfall as mtg
from GSheetUpdater import PriceUpdater


def main():
    # Load cards and update data
    print("Loading cards...")
    cards = mtg.load_card_list()

    print("Updating cards data...")
    cards_data = mtg.update_cards_data(cards)

    CREDENTIALS_PATH = f'./secrets/credentials.json'
    SHEET_NAME = f'Test'

    # Create updater and update prices
    print("Updating prices to gsheet...")
    updater = PriceUpdater(CREDENTIALS_PATH, SHEET_NAME)
    updater.update_prices(cards_data)

    print("Prices updated successfully!")


if __name__ == "__main__":
    main()