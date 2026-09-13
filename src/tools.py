"""
🛠️ TOOL DEFINITIONS & EXECUTION BACKEND
Mã nguồn chứa danh sách Tool Schemas (JSON Schema) và Execution Layer phục vụ cho MCP Server.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    {
        "name": "qc_query",
        "description": "Tra cứu thông tin ca kiểm định và các lỗi gán nhãn 2D/3D bằng mã ca kiểm định.",
        "parameters": {
            "type": "object",
            "properties": {
                "qc_case_id": {
                    "type": "string",
                    "description": "Mã ca kiểm định cần tra cứu (ví dụ: 'QC2026001')"
                }
            },
            "required": ["qc_case_id"]
        }
    },
    # TODO 1.2: Đã hoàn thiện schema cho create_rework_ticket.
    {
        "name": "create_rework_ticket",
        "description": "Tạo phiếu Rework cho ca kiểm định có lỗi gán nhãn 2D/3D cần xử lý lại. Sử dụng qc_query để tra cứu ca kiểm định trước khi tạo phiếu.",
        "parameters": {
            "type": "object",
            "properties": {
                "qc_case_id": {
                    "type": "string",
                    "description": "Mã ca kiểm định cần Rework (ví dụ: 'QC2026001')"
                },
                "annotation_type": {
                    "type": "string",
                    "enum": ["2D", "3D"],
                    "description": "Loại dữ liệu gán nhãn: 2D hoặc 3D."
                },
                "error_description": {
                    "type": "string",
                    "description": "Mô tả lỗi gán nhãn cần xử lý lại."
                },
                "severity": {
                    "type": "string",
                    "enum": ["Minor", "Major", "Critical"],
                    "description": "Mức độ nghiêm trọng của lỗi: Minor, Major hoặc Critical."
                }
            },
            "required": ["qc_case_id", "annotation_type", "error_description", "severity"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "SV2026001": {
        "full_name": "Nguyễn Văn An",
        "class": "AI-K4",
        "gpa": 3.85,
        "email": "an.nv@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "PGS.TS Nguyễn Văn A"
    },
    "SV2026002": {
        "full_name": "Trần Thị Bình",
        "class": "AI-K4",
        "gpa": 3.60,
        "email": "binh.tt@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "TS. Lê Thị B"
    }
}


def execute_academic_query(student_id: str) -> str:
    """Thực thi tra cứu học vụ theo mã sinh viên"""
    student = MOCK_DATABASE.get(student_id.strip().upper())
    if student:
        return json.dumps({
            "status": "SUCCESS",
            "student_id": student_id,
            "data": student
        }, ensure_ascii=False)
    else:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu sinh viên có mã '{student_id}'"
        }, ensure_ascii=False)


def execute_schedule_appointment(student_id: str, datetime_str: str, advisor_name: str = "PGS.TS Nguyễn Văn A") -> str:
    """Thực thi đặt lịch hẹn tư vấn học vụ"""
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"BK-{student_id}-99",
        "student_id": student_id,
        "datetime": datetime_str,
        "advisor": advisor_name,
        "message": f"Đặt lịch thành công cho sinh viên {student_id} với {advisor_name} vào lúc {datetime_str}."
    }, ensure_ascii=False)


# Router gọi tool thực tế
QC_DATABASE = {
    "QC-2026-0913-03": {
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
    },
    "QC-2026-0913-05": {
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
}


def execute_qc_query(qc_case_id: str) -> str:
    """Tra cứu ca kiểm định trong dữ liệu mô phỏng."""
    case_id = qc_case_id.strip()
    case = QC_DATABASE.get(case_id)
    if case:
        return json.dumps({
            "status": "SUCCESS",
            "qc_case_id": case_id,
            "data": case
        }, ensure_ascii=False)
    return json.dumps({
        "status": "NOT_FOUND",
        "message": f"Không tìm thấy ca kiểm định có mã '{qc_case_id}'"
    }, ensure_ascii=False)


def execute_create_rework_ticket(qc_case_id: str, annotation_type: str,
                                 error_description: str, severity: str) -> str:
    """Mô phỏng tạo phiếu Rework, chưa lưu vào hệ thống bên ngoài."""
    from uuid import uuid4

    case_id = qc_case_id.strip()
    case = QC_DATABASE.get(case_id)
    if not case:
        raise ValueError(f"Không tìm thấy ca kiểm định '{qc_case_id}'.")
    if annotation_type not in ("2D", "3D"):
        raise ValueError("annotation_type phải là 2D hoặc 3D.")
    if severity not in ("Minor", "Major", "Critical"):
        raise ValueError("severity phải là Minor, Major hoặc Critical.")
    if not error_description.strip():
        raise ValueError("Mô tả lỗi không được để trống.")

    return json.dumps({
        "status": "SUCCESS",
        "ticket_id": f"RW-{case_id}-{severity.upper()}",
        "qc_case_id": case_id,
        "annotation_type": annotation_type,
        "error_description": error_description.strip(),
        "severity": severity,
        "ticket_status": "Pending"
    }, ensure_ascii=False)

TOOL_ROUTER = {
    "qc_query": execute_qc_query,
    "create_rework_ticket": execute_create_rework_ticket,
    "academic_query": execute_academic_query,
    "schedule_appointment": execute_schedule_appointment
}

def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)
