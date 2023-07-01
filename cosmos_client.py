# import os
# from azure.cosmos import CosmosClient

# def create_cosmos_client():
#     COSMOS_DB_ACCOUNT_URI = os.environ["COSMOS_DB_ACCOUNT_URI"]
#     COSMOS_DB_ACCOUNT_KEY = os.environ["COSMOS_DB_ACCOUNT_KEY"]
#     DATABASE_ID = os.environ['DATABASE_ID']
#     CONTAINER_ID = os.environ['CONTAINER_ID']

#     client = CosmosClient(COSMOS_DB_ACCOUNT_URI, COSMOS_DB_ACCOUNT_KEY)
#     database = client.get_database_client(DATABASE_ID)
#     container = database.get_container_client(CONTAINER_ID)

#     return container
