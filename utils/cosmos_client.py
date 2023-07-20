import os
from azure.cosmos import CosmosClient
import ipinfo
from datetime import datetime
import azure.cosmos.exceptions


def create_cosmos_client():
    COSMOS_DB_ACCOUNT_URI = os.environ["COSMOS_DB_ACCOUNT_URI"]
    COSMOS_DB_ACCOUNT_KEY = os.environ["COSMOS_DB_ACCOUNT_KEY"]
    DATABASE_ID = os.environ["DATABASE_ID"]
    CONTAINER_ID = os.environ["CONTAINER_ID"]

    client = CosmosClient(COSMOS_DB_ACCOUNT_URI, COSMOS_DB_ACCOUNT_KEY)
    database = client.get_database_client(DATABASE_ID)
    container = database.get_container_client(CONTAINER_ID)

    return container


def save_question_answer(container, question, answer, ip):
    handler = ipinfo.getHandler(os.environ["IPINFO_KEY"])

    if ip == "127.0.0.1":
        ip = "83.253.106.168"

    details = handler.getDetails(ip)

    new_chat = {
        "question": question,
        "answer": answer,
    }

    # Retrieve the item if it exists
    try:
        item = container.read_item(item=ip, partition_key=ip)

        # If the item exists, append the new chat
        if "chat" in item:
            if isinstance(item["chat"], list):
                item["chat"].append(new_chat)
            else:
                print(f"Unexpected type for 'chat': {type(item['chat'])}")
                item["chat"] = [new_chat]  # overwrite with a new list
        else:
            item["chat"] = [new_chat]

        container.upsert_item(body=item)

    except azure.cosmos.exceptions.CosmosResourceNotFoundError:
        data = {
            "id": ip,
            "chat": [new_chat],
            "date": datetime.now().isoformat(),
            "city": details.city,
            "region": details.region,
            "country": details.country,
            "loc": details.loc,
            "postal": details.postal,
            "org": details.org,
        }
        container.upsert_item(body=data)
