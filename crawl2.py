from config.ai_config import gemini_client
from const.rag import STORE_NAME

# # my_file_search_store = gemini_client.file_search_stores.get(name='fileSearchStores/algo-store-9ymqlvmoa0vj')
# file_search_store = gemini_client.file_search_stores.create(config={'display_name': 'algo store'})
# # for file_search_store in gemini_client.file_search_stores.list():
# #     print(file_search_store)
# # gemini_client.file_search_stores.delete(name='fileSearchStores/algostore-l4zdkjahkn2z', config={'force': False})
# for file_search_store in gemini_client.file_search_stores.list():
#     print(file_search_store)