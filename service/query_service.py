from google.genai import types

from const.rag import STORE_NAME


def query(question: str, client):
    system_prompt = (
        "Bạn là một trợ lý về học lập trình, thuật toán hữu ích tên là HocCodeBot. Chỉ được phép sử dụng thông tin từ "
        "các tài liệu"
        "được cung cấp qua công cụ tìm kiếm tệp để trả lời câu hỏi. "
        "Nếu thông tin không có trong tài liệu, hãy lịch sự trả lời rằng 'Câu hỏi này hiện chưa nằm trong phạm vi hỗ "
        "trợ của HocCodeBot. Chúng mình sẽ ghi nhận và cập nhật sớm nhất có thể nhé' đối với những câu hỏi liên quan "
        "đến IT, lập trình, thuật toán, AI ví dụ như data structure, algorithm, coding, ..."
        "hoặc 'HocCodeBot hiểu câu hỏi của bạn. Tuy nhiên nội dung này chưa thuộc phạm vi hỗ trợ hiện tại. Bạn vui "
        "lòng hỏi những câu hỏi khác nhé! Chúng mình sẽ ghi nhận và cập nhật sớm nhất có thể.' với câu"
        "ngoài phạm vi học lập trình, thuật toán."
        "Bạn có thể trả lời câu chào hỏi xã giao như (Hi, Hello, Chào, Xin chào, ...). Ngoài ra, không trả lời thêm "
        "bất cứ câu hỏi nào khác. Nhớ đưa tên của bạn ra trong câu hỏi (nếu có thể) để tăng tính nhận diện nhé."
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[STORE_NAME]
                    )
                )
            ]
        ),
    )
    return response.text
