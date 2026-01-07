# from config.ai_config import gemini_client
# from const.rag import STORE_ID
# from google.genai import types
#
#
# class GeminiRAGService:
#     def __init__(self):
#         self.client = gemini_client
#         self.store_id = STORE_ID
#         self.model_id = "gemini-2.0-flash"
#
#     def upload_file_to_store(self, file_path: str, display_name: str):
#         """Upload file và tự động vector hóa vào Store thuật toán"""
#         with open(file_path, "rb") as f:
#             uploaded_file = self.client.files.upload(
#                 file=f,
#                 config={
#                     'display_name': display_name,
#                     'file_search_store_name': self.store_id
#                 }
#             )
#         return uploaded_file
#
#     def delete_file_by_id(self, file_id: str):
#         """Xóa file khỏi kho dữ liệu"""
#         return self.client.files.delete(name=file_id)
#
#     def chat_with_context(self, user_message: str, history: list = None):
#         """Chat dựa trên kiến thức từ file tài liệu thuật toán"""
#         # Cấu hình RAG
#         config = types.GenerateContentConfig(
#             tools=[types.Tool(
#                 file_search=types.FileSearch(index_name=self.store_id)
#             )]
#         )
#
#         # Khởi tạo hoặc tiếp tục phiên chat
#         chat = self.client.chats.create(
#             model=self.model_id,
#             config=config,
#             history=history or []
#         )
#
#         response = chat.send_message(user_message)
#
#         # Trích xuất nguồn tài liệu để hiển thị trên web học tập
#         sources = []
#         if response.candidates[0].grounding_metadata:
#             metadata = response.candidates[0].grounding_metadata
#             if metadata.citations:
#                 sources = [c.source for c in metadata.citations]
#
#         return {
#             "answer": response.text,
#             "sources": list(set(sources)),
#             "new_history": chat.history  # Gửi lại history để client lưu trữ
#         }
