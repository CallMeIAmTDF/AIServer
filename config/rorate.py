# from google.generativeai import client, GenerativeModel
# import threading
#
#
# class GeminiWrapper:
#     def __init__(self, api_key: str, model_name="gemini-2.0-flash"):
#         self.client = client.Client(api_key=api_key)
#         self.model = GenerativeModel(
#             model_name=model_name,
#             client=self.client
#         )
#
#
# class GeminiPool:
#     def __init__(self, api_keys, model_name="gemini-2.0-flash"):
#         self.models = [GeminiWrapper(k, model_name) for k in api_keys]
#         self.index = 0
#         self.lock = threading.Lock()
#
#     def get_model(self):
#         with self.lock:
#             model = self.models[self.index].model
#             self.index = (self.index + 1) % len(self.models)
#             return model
