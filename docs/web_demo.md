# QC Assistant — Web demo

Chạy từ thư mục gốc dự án trên Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -B src/web_demo.py
```

Mở http://127.0.0.1:8000. Dừng bằng `Ctrl+C`.
Nếu cổng đang được sử dụng, thêm `--port 8001` và mở cổng tương ứng.
HTTP server dùng thư viện chuẩn Python; ô chat dùng OpenAI SDK và python-dotenv đã có trong requirements.txt. Cần `LLM_PROVIDER=openai` và API key hợp lệ cho ô chat.

## Luồng sử dụng

Ô **Trợ lý kiểm định chất lượng** ở đầu trang gọi OpenAI API thật qua `/api/agent`. Chọn câu hỏi mẫu rồi nhấn **Gửi yêu cầu**. Mỗi yêu cầu độc lập, cần ghi rõ mã ca. Kết quả có phần mở rộng xem các bước hành động và số lượt API/MCP. Phiếu do Agent tạo được đưa vào mục **Phiếu Rework** để xuất JSON. Nếu API lỗi, web báo lỗi, không fallback Mock.

Ví dụ: “Kiểm tra ca QC-2026-0913-05 và tạo phiếu Rework cho lỗi mức độ Critical. Ghi rõ số frame.”

Ngoài chat, có thể thao tác thủ công:

1. Chọn ca trong danh sách hoặc tra cứu mã đầy đủ, ví dụ `QC-2026-0913-05`.
2. Dùng bộ lọc 2D/3D để lọc danh sách. Xem frame, loại lỗi, mức độ và người phụ trách trong chi tiết ca.
3. Nhấn **Dùng lỗi này**, chỉnh mô tả và mức độ, sau đó nhấn **Tạo phiếu Rework**.
4. Mở **Phiếu Rework** để xem kết quả và xuất từng phiếu JSON.

## Phạm vi demo

- `src/web_demo.py`: HTTP server cục bộ, cung cấp API tra cứu và tạo phiếu qua `MCPAcademicServer.call_tool` hiện có.
- `src/web_demo.html`: giao diện tiếng Việt, bố cục thích ứng màn hình và JavaScript gọi API.
- Danh sách ca lấy từ `QC_DATABASE` hiện có. Trước khi tạo phiếu, server tra cứu lại ca qua `qc_query`.
- Phiếu được lưu bằng localStorage trên trình duyệt hiện tại, không gửi tới hệ thống sản xuất. Xóa dữ liệu trình duyệt sẽ mất phiếu; có thể xuất JSON để giữ bản sao.
- Ô chat dùng LLM thật; form tra cứu và tạo phiếu thủ công gọi công cụ trực tiếp. Dữ liệu QC/MCP và phiếu vẫn mô phỏng.
- Các thư mục dự án và luồng CLI hiện có được giữ nguyên.

## Kiểm tra đã thực hiện

## Kịch bản trình diễn API thật

Web đã có ô chat gọi LLM thật. Để chạy thêm bộ nghiệm thu 5 ca và xuất báo cáo, dùng terminal:

```powershell
.\.venv\Scripts\python.exe -B src/check_live_demo.py
```

Lệnh này chạy 5 ca bằng API thật, tắt fallback Mock, kiểm tra luồng công cụ và ghi `docs/live_demo_check.json`. Mỗi lượt có thể phát sinh nhiều yêu cầu LLM vì Agent nhận lại Observation trước khi quyết định bước tiếp theo. Cần mạng truy cập OpenAI và API key hợp lệ trong `.env` với `LLM_PROVIDER=openai`. Không hiển thị `.env` khi trình chiếu.

Kịch bản demo khoảng 3 phút:

1. Mở web, chọn `QC-2026-0913-05`, chỉ ra lỗi Minor ở frame 42 và Critical ở frame 89.
2. Chọn lỗi 3D ở frame 89, tạo phiếu, xem mục Phiếu Rework và xuất JSON.
3. Dùng ô chat yêu cầu tạo Rework cho lỗi Critical. Mở quá trình xử lý: LLM gọi `qc_query`, nhận dữ liệu, gọi `create_rework_ticket`, rồi trả lời mã phiếu. Phiếu xuất hiện trong mục Phiếu Rework.
4. Chỉ ra TC05: mã không tồn tại phải trả `NOT_FOUND`, không tạo phiếu.
5. Mở báo cáo để xem `live_api_successes`, `mcp_calls` và kết quả từng ca. Đây là kiểm tra luồng công cụ, không phải chứng nhận mọi nội dung câu trả lời đều đúng.

API LLM là thật; dữ liệu QC và việc tạo Rework vẫn mô phỏng. Phiếu tạo trong terminal không tự xuất hiện trong localStorage của web.

Trang chủ và API danh sách trả HTTP 200; tra cứu qua MCP trả đúng ca; tạo phiếu trả kết quả thành công và mã riêng biệt; đầu vào sai mức độ, sai loại nhãn, mô tả trống và mã ca không tồn tại đều bị từ chối. JavaScript đã qua kiểm tra cú pháp. Chưa kiểm thử tương tác trực tiếp trên trình duyệt.

Kiểm tra HTTP chat với API thật: TC02 tra cứu (2 lượt API / 1 MCP), TC04 tạo Rework Critical frame 89 (3 API / 2 MCP), TC05 không tìm thấy ca (2 API / 1 MCP) đều đạt; đầu vào rỗng trả HTTP 400. Không có trình duyệt kết nối trong phiên kiểm tra. Bản demo chat hiện chạy ở http://127.0.0.1:8001; cổng 8000 có thể vẫn là tiến trình cũ.
