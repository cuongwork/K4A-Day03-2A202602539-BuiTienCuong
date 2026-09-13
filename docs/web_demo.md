# QC Assistant — Web demo

Chạy từ thư mục gốc dự án trên Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -B src/web_demo.py
```

Mở http://127.0.0.1:8000. Dừng bằng `Ctrl+C`.
Nếu cổng đang được sử dụng, thêm `--port 8001` và mở cổng tương ứng.
Demo chỉ dùng thư viện chuẩn Python, không cần cài thêm dependency.

## Luồng sử dụng

1. Chọn ca trong danh sách hoặc tra cứu mã đầy đủ, ví dụ `QC-2026-0913-05`.
2. Dùng bộ lọc 2D/3D để lọc danh sách. Xem frame, loại lỗi, mức độ và người phụ trách trong chi tiết ca.
3. Nhấn **Dùng lỗi này**, chỉnh mô tả và mức độ, sau đó nhấn **Tạo phiếu Rework**.
4. Mở **Phiếu Rework** để xem kết quả và xuất từng phiếu JSON.

## Phạm vi demo

- `src/web_demo.py`: HTTP server cục bộ, cung cấp API tra cứu và tạo phiếu qua `MCPAcademicServer.call_tool` hiện có.
- `src/web_demo.html`: giao diện tiếng Việt, bố cục thích ứng màn hình và JavaScript gọi API.
- Danh sách ca lấy từ `QC_DATABASE` hiện có. Trước khi tạo phiếu, server tra cứu lại ca qua `qc_query`.
- Phiếu được lưu bằng localStorage trên trình duyệt hiện tại, không gửi tới hệ thống sản xuất. Xóa dữ liệu trình duyệt sẽ mất phiếu; có thể xuất JSON để giữ bản sao.
- Đây là giao diện thao tác công cụ với MCP Server mô phỏng; không gọi LLM hoặc yêu cầu API key.
- Các thư mục dự án và luồng CLI hiện có được giữ nguyên.

## Kiểm tra đã thực hiện

Trang chủ và API danh sách trả HTTP 200; tra cứu qua MCP trả đúng ca; tạo phiếu trả kết quả thành công và mã riêng biệt; đầu vào sai mức độ, sai loại nhãn, mô tả trống và mã ca không tồn tại đều bị từ chối. JavaScript đã qua kiểm tra cú pháp. Chưa kiểm thử tương tác trực tiếp trên trình duyệt.
