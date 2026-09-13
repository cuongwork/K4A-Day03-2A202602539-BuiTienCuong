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
## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Hãy tạo phiếu Rework cho ca kiểm định QC-2026-0913-03, lỗi gán nhãn 3D sai vị trí Bounding Box tại Frame 125, mức độ lỗi Major.",
    "action_type": "TOOL_EXECUTION",
    "decision_summary": "Thực thi công cụ qc_query do LLM đề xuất.",
    "summary_source": "application",
    "tool_name": "qc_query",
    "arguments": {
      "qc_case_id": "QC-2026-0913-03"
    },
    "observation": {
      "status": "SUCCESS",
      "qc_case_id": "QC-2026-0913-03",
      "data": {
        "qc_case_id": "QC-2026-0913-03",
        "status": "IN_REVIEW",
        "annotation_errors": [
          {
            "annotation_type": "3D",
            "frame": 125,
            "error_type": "Bounding Box sai vị trí",
            "severity": "Major",
            "responsible_person": "Nguyễn Văn An"
          }
        ]
      }
    },
    "latency_ms": 893.09,
    "test_case_id": "TC03",
    "provider": "OpenAIProvider",
    "model": "gpt-4o-mini",
    "run_at": "2026-09-13T04:31:07.718329+00:00",
    "source_artifact": "docs/live_demo_check.json"
  },
  {
    "step": 2,
    "query": "Hãy tạo phiếu Rework cho ca kiểm định QC-2026-0913-03, lỗi gán nhãn 3D sai vị trí Bounding Box tại Frame 125, mức độ lỗi Major.",
    "action_type": "TOOL_EXECUTION",
    "decision_summary": "Thực thi công cụ create_rework_ticket do LLM đề xuất.",
    "summary_source": "application",
    "tool_name": "create_rework_ticket",
    "arguments": {
      "qc_case_id": "QC-2026-0913-03",
      "annotation_type": "3D",
      "error_description": "Bounding Box sai vị trí tại Frame 125",
      "severity": "Major"
    },
    "observation": {
      "status": "SUCCESS",
      "ticket_id": "RW-QC-2026-0913-03-MAJOR",
      "qc_case_id": "QC-2026-0913-03",
      "annotation_type": "3D",
      "error_description": "Bounding Box sai vị trí tại Frame 125",
      "severity": "Major",
      "ticket_status": "Pending"
    },
    "latency_ms": 800.97,
    "test_case_id": "TC03",
    "provider": "OpenAIProvider",
    "model": "gpt-4o-mini",
    "run_at": "2026-09-13T04:31:07.718329+00:00",
    "source_artifact": "docs/live_demo_check.json"
  },
  {
    "step": 3,
    "query": "Hãy tạo phiếu Rework cho ca kiểm định QC-2026-0913-03, lỗi gán nhãn 3D sai vị trí Bounding Box tại Frame 125, mức độ lỗi Major.",
    "action_type": "FINAL_ANSWER",
    "decision_summary": "Tổng hợp phản hồi từ các Observation đã nhận.",
    "summary_source": "application",
    "raw_model_output": "Phiếu Rework đã được tạo thành công cho ca kiểm định QC-2026-0913-03 với lỗi \"Bounding Box sai vị trí tại Frame 125\" và mức độ lỗi Major. Mã phiếu Rework là: **RW-QC-2026-0913-03-MAJOR**.",
    "output_policy": "model_response",
    "output": "Phiếu Rework đã được tạo thành công cho ca kiểm định QC-2026-0913-03 với lỗi \"Bounding Box sai vị trí tại Frame 125\" và mức độ lỗi Major. Mã phiếu Rework là: **RW-QC-2026-0913-03-MAJOR**.",
    "latency_ms": 1032.29,
    "test_case_id": "TC03",
    "provider": "OpenAIProvider",
    "model": "gpt-4o-mini",
    "run_at": "2026-09-13T04:31:07.718329+00:00",
    "source_artifact": "docs/live_demo_check.json"
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [ v] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 6 lượt.
- **Kết quả đẩy Repo nộp bài:** [v ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
