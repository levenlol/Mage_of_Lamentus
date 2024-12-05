import sys, os
ROOT_DIR = os.path.join(os.getcwd(), 'src')

sys.path.append(ROOT_DIR)
import mtg_scraper_scryfall as mtg

def main():
    cards = mtg.load_card_list()
    cards_data = mtg.update_cards_data(cards)


if __name__ == "__main__":
    main()