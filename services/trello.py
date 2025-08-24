import requests
import os

def create_trello_card(card_name, card_desc):
    """
    Creates a new card on a Trello board using environment variables for credentials.
    """
    url = "https://api.trello.com/1/cards"

    trello_api_key = os.getenv("TRELLO_API_KEY")
    trello_token = os.getenv("TRELLO_TOKEN")
    trello_board_id = os.getenv("TRELLO_BOARD_ID")
    trello_list_id = os.getenv("TRELLO_LIST_ID")

    query = {
        'key': trello_api_key,
        'token': trello_token,
        'idList': trello_list_id,
        'idBoard': trello_board_id,
        'name': card_name,
        'desc': card_desc
    }
    
    try:
        response = requests.request("POST", url, params=query)
        if response.status_code == 200:
            print("Trello card created successfully!")
        else:
            print(f"Failed to create Trello card. Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the Trello API request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during Trello card creation: {e}")

