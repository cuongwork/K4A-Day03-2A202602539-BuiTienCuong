# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Bùi Tiến Cường  
> **Mã Sinh Viên / Mã Học viên:** 2A202602539  
> **Chủ đề Lựa chọn:** Trợ lý Kiểm định Chất lượng (QC Assistant): Tra cứu ca lỗi gán nhãn 2D/3D và tạo phiếu Rework kiểm định.]  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4/ 5 | Bài toán có yêu cầu chia nhỏ nhiều bước suy luận nối tiếp nhau không? Có chuỗi xử lý tương đối rõ: nhận yêu cầu → xác định ca/lô cần kiểm tra → truy xuất dữ liệu lỗi 2D/3D → phân loại/đối chiếu lỗi → xác định đối tượng cần Rework → tổng hợp thông tin → tạo phiếu Rework.|
| **2. Tool Interaction** | 4/ 5 | Hệ thống có cần kết nối với MCP Server / Cơ sở dữ liệu bên ngoài không? Cần tương tác mạnh với hệ thống bên ngoài để xác định đối chiếu thông tin, dữ liệu |
| **3. Dynamic Decision** | 5/ 5 | Bước tiếp theo có phụ thuộc vào kết quả quan sát bước trước không? có. Vì nếu không tìm thấy lỗi thì không tạo Rework; nếu lỗi vượt ngưỡng hoặc thuộc nhóm nghiêm trọng thì cần tạo phiếu; nếu dữ liệu thiếu thì phải truy vấn bổ sung hoặc chuyển  sang kiểm tra thủ công. |
| **4. Long Horizon Goal** | 4/ 5 | Hệ thống có phải giữ mục tiêu xuyên suốt qua nhiều lượt xử lý không? cần giữ mục tiêu xuyên suốt từ lúc xác định lỗi đến khi tạo và hoàn thành rework kiểm định |
| **TỔNG ĐIỂM AGENTIC FIT** | 17 **/ 20** | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. K?T QU? KI?M TH? TR?N API TH?T

- Th?i ?i?m b?t ??u (UTC): `2026-09-13T04:31:07.718329+00:00`.
- Provider: **OpenAIProvider**; model c?u h?nh: **gpt-4o-mini**.
- S? l??t g?i API LLM th?nh c?ng: **11 l??t**.
- S? l??t g?i Tool qua MCP Server: **6 l??t** (4 l?n `qc_query`, 2 l?n `create_rework_ticket`).
- K?t qu?: **5/5 ca ??t c?c ki?m tra t? ??ng ?? khai b?o**: lu?ng c?ng c?, c?c tr??ng k?t qu? ch?nh v? c?u tr?c trace.
- L?nh ki?m th?: `.\.venv\Scripts\python.exe -B src/check_live_demo.py`.
- B?ng ch?ng: [b?o c?o API th?t](live_demo_check.json), [Waterfall trace](trace_waterfall.json), [test cases](../config/test_cases.json).

B? ch?y nghi?m thu d?ng OpenAI SDK tr?c ti?p v?i Native Tool Calling, kh?ng fallback Mock. M?i ph?n h?i th?nh c?ng c? `response_id`, model th?c t? v? s? token trong `api_responses`. S? l??t tr?n ch? t?nh l?n ch?y n?y, kh?ng c?ng c?c l?n th? tr??c.

| Ca | N?i dung ki?m tra | Lu?ng c?ng c? th?c t? | K?t qu? |
| :--- | :--- | :--- | :--- |
| TC01 | Gi?i thi?u quy tr?nh QC 2D/3D | Kh?ng g?i tool | ??t |
| TC02 | Tra c?u ca QC-2026-0913-05 | qc_query | ??t |
| TC03 | T?o Rework 3D, Major, frame 125 | qc_query ? create_rework_ticket | ??t |
| TC04 | Tra c?u r?i t?o Rework cho Critical, frame 89 | qc_query ? create_rework_ticket | ??t |
| TC05 | M? kh?ng t?n t?i; ch?a th? x?c ??nh nhu c?u Rework | qc_query | ??t |

TC03 ??ng b? ??ng b?n tham s? c?a schema: `qc_case_id`, `annotation_type`, `error_description`, `severity`. S? frame n?m trong m? t? l?i; kh?ng y?u c?u tham s? ng??i ph? tr?ch.

## 3. TR?CH WATERFALL TRACE TC04

Y?u c?u: ki?m tra ca `QC-2026-0913-05`, ch? t?o Rework cho l?i Major ho?c Critical. Observation cho bi?t c? l?i 2D Minor t?i frame 42 v? l?i 3D Critical t?i frame 89; Agent t?o m?t phi?u cho l?i Critical.

`decision_summary` l? t?m t?t quy?t ??nh do ?ng d?ng ghi t? h?nh ??ng quan s?t ???c (`summary_source=application`), thay cho nh?n Thought. Kh?ng l?u suy lu?n n?i b? c?a model. M?i b??c c?ng c? ch?a Action (`tool_name`, `arguments`) v? Observation ??y ??; b??c cu?i ch?a Final Answer (`output`).

?o?n d??i tr?ch c?c tr??ng li?n quan tr?c ti?p t? trace m?i, kh?ng ph?i log m?u:

```json
[
  {
    "step": 1,
    "decision_summary": "Thực thi công cụ qc_query do LLM đề xuất.",
    "summary_source": "application",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "qc_query",
    "arguments": {
      "qc_case_id": "QC-2026-0913-05"
    },
    "observation": {
      "status": "SUCCESS",
      "qc_case_id": "QC-2026-0913-05",
      "data": {
        "qc_case_id": "QC-2026-0913-05",
        "status": "IN_REVIEW",
        "annotation_errors": [
          {
            "annotation_type": "2D",
            "frame": 42,
            "error_type": "Màu nhãn không khớp",
            "severity": "Minor",
            "responsible_person": "Trần Thị Bình"
          },
          {
            "annotation_type": "3D",
            "frame": 89,
            "error_type": "Bounding Box lệch góc",
            "severity": "Critical",
            "responsible_person": "Nguyễn Văn An"
          }
        ]
      }
    },
    "latency_ms": 1384.82
  },
  {
    "step": 2,
    "decision_summary": "Thực thi công cụ create_rework_ticket do LLM đề xuất.",
    "summary_source": "application",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "create_rework_ticket",
    "arguments": {
      "qc_case_id": "QC-2026-0913-05",
      "annotation_type": "3D",
      "error_description": "Bounding Box lệch góc tại frame 89",
      "severity": "Critical"
    },
    "observation": {
      "status": "SUCCESS",
      "ticket_id": "RW-QC-2026-0913-05-CRITICAL",
      "qc_case_id": "QC-2026-0913-05",
      "annotation_type": "3D",
      "error_description": "Bounding Box lệch góc tại frame 89",
      "severity": "Critical",
      "ticket_status": "Pending"
    },
    "latency_ms": 846.02
  },
  {
    "step": 3,
    "decision_summary": "Tổng hợp phản hồi từ các Observation đã nhận.",
    "summary_source": "application",
    "action_type": "FINAL_ANSWER",
    "output": "Đã kiểm tra ca kiểm định QC-2026-0913-05 và phát hiện một lỗi mức độ Critical:\n\n- **Loại dữ liệu gán nhãn**: 3D\n- **Mô tả lỗi**: Bounding Box lệch góc tại frame 89\n\nPhiếu Rework đã được tạo thành công với mã phiếu: **RW-QC-2026-0913-05-CRITICAL**. \n\nNếu bạn cần thêm thông tin hoặc hỗ trợ khác, hãy cho tôi biết!",
    "latency_ms": 1182.8
  }
]
```

## 4. KI?M SO?T TR??NG H?P KH?NG T?M TH?Y CA

TC05 nh?n `NOT_FOUND`, kh?ng g?i c?ng c? t?o phi?u. Ph?n h?i cu?i:

> Không tìm thấy ca kiểm định QC-INVALID-99999. Chưa thể xác định lỗi hoặc nhu cầu Rework vì không có dữ liệu ca kiểm định. Vui lòng kiểm tra lại mã ca.

?ng d?ng ?p d?ng `output_policy=not_found_guard` ?? kh?ng bi?n vi?c thi?u d? li?u th?nh k?t lu?n kh?ng c? l?i. Trace gi? `raw_model_output` ri?ng ?? ph?n bi?t c?u tr? l?i nguy?n b?n c?a API v?i ph?n h?i ?? ???c ?ng d?ng chu?n h?a; kh?ng s?a ?m th?m b?ng ch?ng c?a model.

## 5. T?NG K?T NGHI?M THU V? GI?I H?N

- [x] ?? x?c minh OpenAI API th?t trong l?n ch?y nghi?m thu ???c ghi ? tr?n.
- [x] T?ng s? Test Cases ??t ki?m tra t? ??ng: **5/5**.
- [x] S? l??t API LLM th?nh c?ng: **11 l??t**.
- [x] S? l??t g?i tool qua MCP Server: **6 l??t**; TC05 tr? `NOT_FOUND` ??ng k? v?ng, kh?ng ph?i l?i ki?m th?.
- [x] Waterfall ch?a **11 s? ki?n**, g?m **6 Action/Observation** v? **5 Final Answer**, c? m? test case v? t?m t?t quy?t ??nh.
- [ ] Commit v? push GitHub: ch?a x?c minh trong l?n nghi?m thu n?y.

Ph?m vi b?ng ch?ng v? gi?i h?n:

- API LLM l? th?t; MCP Server, c? s? d? li?u QC v? vi?c t?o phi?u v?n m? ph?ng c?c b?.
- Ki?m th? x?c nh?n c?c ?i?u ki?n ???c m? h?a, kh?ng ch?ng nh?n to?n b? n?i dung ng?n ng? t? nhi?n lu?n ??ng. K?t qu? c? th? thay ??i gi?a c?c l?n g?i model.
- Agent hi?n ??a Observation v?o ng? c?nh v?n b?n ? l??t ti?p theo; ch?a d?ng l?ch s? `tool` message k?m `tool_call_id` xuy?n su?t.
- T?m t?t quy?t ??nh do ?ng d?ng t?o; kh?ng ???c coi l? suy lu?n n?i b? ???c model ti?t l?.
- Demo ch? cho ph?p c?ng c? t?o phi?u khi y?u c?u ti?ng Vi?t ch?a ?t?o? v? ?rework?. ??y l? gi?i h?n nh?n di?n ? ??nh c?a demo, ch?a ph?i b? ph?n lo?i cho m?i c?ch di?n ??t.
- Web demo g?i c?ng c? tr?c ti?p; lu?ng Agent d?ng LLM th?t ???c ch?y qua terminal.
- Provider th?ng th??ng v?n c? fallback Mock khi API l?i; b?o c?o n?y d?ng b? ki?m tra nghi?m ng?t kh?ng fallback. Ch?y phi?n CLI kh?c c? th? ghi ?? Waterfall; ch?y l?i l?nh nghi?m thu ?? ??ng b? artifact tr??c khi n?p.
