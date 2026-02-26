import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MONDAY_API_KEY")
DEALS_BOARD_ID = os.getenv("DEALS_BOARD_ID")
WORK_ORDERS_BOARD_ID = os.getenv("WORK_ORDERS_BOARD_ID")

headers = {"Authorization": API_KEY, "Content-Type": "application/json"}
api_url = "https://api.monday.com/v2"

def fetch_board_data(board_id):
    query = f"""
    {{
      boards(ids: {board_id}) {{
        items_page(limit: 500) {{
          items {{
            id
            name
            column_values {{
              column {{ title }}
              text
            }}
          }}
        }}
      }}
    }}
    """
    response = requests.post(api_url, json={"query": query}, headers=headers)
    if response.status_code != 200:
        raise Exception(f"API error: {response.text}")
    data = response.json()
    items = []
    for item in data.get("data", {}).get("boards", [])[0].get("items_page", {}).get("items", []):
        row = {"id": item["id"], "name": item["name"]}
        for col in item["column_values"]:
            title = col["column"]["title"]
            value = col["text"]
            row[title] = value
        items.append(row)
    return items

def get_deals():
    return fetch_board_data(DEALS_BOARD_ID)

def get_work_orders():
    return fetch_board_data(WORK_ORDERS_BOARD_ID)