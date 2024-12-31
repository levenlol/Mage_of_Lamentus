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
        
        # mage of lamentus doc link.
        url = "https://docs.google.com/spreadsheets/d/1T71vR-M9ut3xvDamhMEr8iTymTA1mneLmsesDyeyxnY/edit?gid=0#gid=0"

        # Open the spreadsheet
        self.sheet = client.open_by_url(url).sheet1



    def update_prices(self, price_data):
        """
        Update prices in the Google Sheet
        
        :param price_data: List of tuples (name, price_usd, price_eur)
        """
        # Get all existing records
        head = 4
        existing_records = self.sheet.get_all_records(head=head)
        
        for data in price_data:
            # Try to find existing record
            name, price_usd, price_eur = data['name'], data['price_usd'], data['price_eur']
            set_code, collector_number = data['set_code'], data['collector_number']
            uri = data['uri']

            name = name + " (" + set_code + ") " + collector_number
            hname = f'=HYPERLINK("{uri}"; "{name}")'

            existing_record = None
            for idx, record in enumerate(existing_records):  # Start at 5 because of header row and other infos
                if record['Card Name'] == name:
                    existing_record = (idx, record)
                    break
            
            if existing_record:
                # Update existing record
                row_idx, record = existing_record
                self.sheet.update_cell(row_idx + head + 1, 5, price_usd)  # Update current USD price
                self.sheet.update_cell(row_idx + head + 1, 4, price_eur)  # Update current EUR price
            else:
                # Add new record
                new_row = [
                    hname,  # name
                    price_eur,  # start price EUR
                    price_usd,  # start price USD
                    price_eur,   # current price EUR
                    price_usd  # current price USD
                ]
                self.sheet.append_row(new_row,value_input_option='USER_ENTERED')



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