import gspread
from oauth2client.service_account import ServiceAccountCredentials

class PriceUpdater:
    def __init__(self, credential_path, sheet_name):
        """
        Initialize the Google Sheets price updater
        
        :param credentials_path: Path to the Google Cloud service account JSON key file
        :param sheet_name: Name of the Google Sheet to update
        """
        # Set up the credentials
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        # Authenticate and get the spreadsheet
        creds = ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)
        client = gspread.authorize(creds)
        
        url = "https://docs.google.com/spreadsheets/d/1CD867FiqKXMxrvW-ogIfVaGCkl5zxk6ka2tuXA9yx_4/edit?gid=0#gid=0"

        # Open the spreadsheet
        self.sheet = client.open_by_url(url).sheet1



    def update_prices(self, price_data):
        """
        Update prices in the Google Sheet
        
        :param price_data: List of tuples (name, price_usd, price_eur)
        """
        # Get all existing records
        existing_records = self.sheet.get_all_records()
        
        for name, price_usd, price_eur in price_data:
            # Try to find existing record
            existing_record = None
            for idx, record in enumerate(existing_records, start=2):  # Start at 2 because of header row
                if record['name'] == name:
                    existing_record = (idx, record)
                    break
            
            if existing_record:
                # Update existing record
                row_idx, record = existing_record
                self.sheet.update_cell(row_idx, 4, price_usd)  # Update current USD price
                self.sheet.update_cell(row_idx, 5, price_eur)  # Update current EUR price
            else:
                # Add new record
                new_row = [
                    name,  # name
                    price_usd,  # start price USD
                    price_eur,  # start price EUR
                    price_usd,  # current price USD
                    price_eur   # current price EUR
                ]
                self.sheet.append_row(new_row)
                existing_records.append(dict(zip(['name', 'startpriceusd', 'startpriceeur', 'currentpriceusd', 'currentpriceeur'], new_row)))


def main():
    CREDENTIALS_PATH = f'./secrets/credentials.json'
    SHEET_NAME = f'Test'

     # Sample price data
    price_data = [
        ('Apple', 250.50, 240.25),
        ('Google', 120.75, 110.50),
        ('Microsoft', 300.25, 280.75)
    ]

    # Create updater and update prices
    updater = PriceUpdater(CREDENTIALS_PATH, SHEET_NAME)
    updater.update_prices(price_data)

    print("Prices updated successfully!")


if __name__ == '__main__':
    main()