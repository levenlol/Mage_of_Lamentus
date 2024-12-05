import sys, os
ROOT_DIR = os.path.join(os.getcwd(), 'src')

sys.path.append(ROOT_DIR)
from mtg_scraper_scryfall import ScryfallPriceScraper
import tkinter as tk
from tkinter import messagebox
from datetime import date

import re

def show_error(message):
    """Create a top-most error dialog."""
    root = tk.Tk()
    root.attributes('-topmost', True)  # Ensure top-most window
    root.withdraw()  # Hide the main window
    messagebox.showerror("Error", message, parent=root)
    root.destroy()

def validate_cards(card_name, expansion, number):
    """
    Validate card name input.
    Prevents offensive or invalid names.
    """

    cards = ScryfallPriceScraper.get_card_prices(card_name, expansion if expansion != '_' else "", number if number != '_' else "")

    if len(cards) == 0:
        show_error(f"Invalid card name: {card_name} set: {expansion} number: {number}")
        return []
        
    print(f"Found: {len(cards)} with name: {card_name}.")
    return cards


def parse_string(input_string):
    # Simplified parsing based on the given rules
    name, set_part, num = "", "", ""

    # Find the index of '(' and ')'
    open_paren_index = input_string.find("(")
    close_paren_index = input_string.find(")")

    if open_paren_index != -1:  # If '(' exists
        name = input_string[:open_paren_index]  # Everything before '(' is NAME
        if close_paren_index != -1:  # If ')' also exists
            set_part = input_string[open_paren_index + 1:close_paren_index]  # Inside '()' is SET
            num = input_string[close_paren_index + 1:]  # Everything after ')' is NUM
        else:
            raise ValueError("Unmatched '(' without a closing ')'.")
    else:
        name = input_string  # If no '(', entire string is NAME

    return name, set_part, num

def log_card_collection(filename='data/cards_list.txt'):
    """
    Log card information to a text file with specified format:
    Card_Name | expansion_code | collector_number | uri
    
    Stops when an empty card name is entered.
    """
    try:
        with open(filename, 'r') as existing_file:
            unique_lines = set(existing_file.readlines())
    except FileNotFoundError:
        unique_lines = set()

    with open(filename, 'a', encoding='utf-8') as file:
        while True:
            # Get card name (mandatory)
            card_name = input("Enter card name (optional Card_Name(SET)#): ").strip()
            if not card_name:
                break
            
            card_name, expansion_code, card_number = parse_string(card_name)

            # Write to file
            today = date.today().strftime('%d/%m/%Y')
            cards = validate_cards(card_name, expansion_code, card_number)
            for card in cards:
                line_id = f"{card['name']} | {card['set']} | {card['collector_number']} | "
                line = f"{card['prices']['usd']} | {card['prices']['usd_foil']} | "
                line += f"{card['prices']['eur']} | {card['prices']['eur_foil']} | "
                line += f"{card['prices']['tix']} | {today} | {card['uri']}\n"

                if line_id not in unique_lines:
                    unique_lines.add(line_id)
                    file.write(line_id + line)
                else:
                    print(f"{card['name']}({card['set']}) already present.")

    print(f"Card collection logged to {filename}")

# Run the script
if __name__ == "__main__":
    log_card_collection()