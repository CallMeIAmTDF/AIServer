# AIServer

AIServer là backend API server viết bằng **Python** và được chạy bằng **uvicorn**.  
Dự án **bắt buộc cần Perl** vì một số chức năng trong server gọi trực tiếp các script Perl có trong repository.

README này được viết **dựa trên source code hiện có**, không mô tả ngoài phạm vi repo.

---

## Yêu cầu môi trường

Để chạy AIServer, hệ thống cần có:

- Python 3.10+
- Perl (bắt buộc)
- pip (Python package manager)

---

## Cấu hình môi trường (.env)

Project sử dụng biến môi trường để cấu hình runtime.  
Tạo file `.env` tại thư mục gốcc:

---

## Cài đặt

Clone repository:

```bash
git clone https://github.com/CallMeIAmTDF/AIServer.git
cd AIServer
```

Tạo virtual environment (khuyến nghị):

```bash
python -m venv venv
source venv/bin/activate
```

Cài đặt các thư viện Python:

```bash
pip install -r requirements.txt
```

Kiểm tra Perl đã sẵn sàng:

```bash
perl -v
```

Nếu chưa có Perl (Ubuntu/Debian):

```bash
sudo apt update
sudo apt install perl
```

---

## Chạy server

AIServer được khởi chạy bằng **uvicorn**, với entry point là `app:api`.

Chạy lệnh sau tại thư mục gốc của project:

```bash
uvicorn app:api
```

Khi develop:

```bash
uvicorn app:api --reload
```

---

## Perl trong dự án

Repo có các file Perl (ví dụ: `moss.pl`) được server gọi trong quá trình xử lý logic.  
Vì vậy **Perl là dependency bắt buộc**, kể cả khi server chính chạy bằng Python.

Server sẽ không hoạt động đúng nếu Perl không được cài đặt hoặc không truy cập được script Perl.

---

## Ghi chú

- Project này tập trung vào **API server**
- Không tự động cài Perl hay dependency hệ thống
- Người dùng chịu trách nhiệm chuẩn bị môi trường phù hợp

