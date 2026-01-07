def create_file_search_store(client, display_name: str):
    store = client.file_search_stores.create(
        config={
            "display_name": display_name
        }
    )
    return store.name
