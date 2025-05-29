import re
from typing import Any

from agno.agent import Agent
from agno.team.team import Team
from pydantic import BaseModel, Field
from agno.models.openai import OpenAIChat

from dotenv import load_dotenv
load_dotenv()

model = OpenAIChat(id="gpt-4o")

class CodeAndTestRequirements(BaseModel):
    """Định dạng kết quả cuối cùng cho code_requirement và test_requirement."""
    code_requirement: str = Field(
        description="Mô tả chính xác những gì hàm hoặc đoạn mã cần làm.")
    test_requirement: str = Field(
        description="Mô tả các LOẠI trường hợp kiểm thử cần được tạo ra, không chứa các giá trị cụ thể.")
    

class TestCaseItem(BaseModel):
    """Mô tả cấu trúc của một test case đơn lẻ."""
    input: Any = Field(
        description="Giá trị đầu vào cho hàm. Có thể là một giá trị đơn hoặc một list/tuple nếu hàm nhận nhiều đối số.")
    expected_output: Any = Field(description="Giá trị đầu ra mong đợi từ hàm.")


def run_python_code(code: str, test_cases: list[TestCaseItem]) -> dict:
    """
    Thực thi mã Python với các test cases đã cho và trả về kết quả.
    An toàn khi thực thi mã trong một môi trường sandbox.
    
    Args:
        code (str): Chuỗi mã Python cần thực thi.
        test_cases (List[TestCaseItem]): Danh sách các đối tượng TestCaseItem, mỗi đối tượng chứa 'input' và 'expected_output'.
                            Ví dụ: [{'input': [2, 3], 'expected_output': 5}]
                            Đối với input, nếu hàm nhận nhiều đối số, hãy đặt chúng trong một tuple hoặc list.
                            Ví dụ: input: (2, 3) cho hàm func(a, b).

    Returns:
        dict: Kết quả kiểm thử. Ví dụ:
            {
                "success": bool,
                "results": [
                    {"test_case": dict, "passed": bool, "actual_output": any, "error": str},
                    ...
                ]
            }
    """
    print("\n--- Executing Code ---")
    print(f"Code:\n{code}\n")
    # Chuyển đổi TestCaseItem Pydantic objects thành dicts để tương thích với logic hiện tại
    # hoặc điều chỉnh logic để làm việc trực tiếp với TestCaseItem.
    # Hiện tại, tôi sẽ chuyển đổi để giữ logic thực thi không đổi.
    test_cases_dicts = [tc.model_dump() if isinstance(
        tc, BaseModel) else tc for tc in test_cases]
    print(f"Test Cases: {test_cases_dicts}\n")

    results = []
    overall_success = True

    exec_globals = {}
    try:
        exec(code, exec_globals)
    except Exception as e:
        return {"success": False, "results": [], "error": f"Error compiling code: {e}"}

    function_name = None
    match = re.search(r"def (\w+)\(", code)
    if match:
        function_name = match.group(1)
        target_function = exec_globals.get(function_name)

        if not callable(target_function):
            return {"success": False, "results": [], "error": f"Function '{function_name}' not found or not callable after compilation."}
    else:
        return {"success": False, "results": [], "error": "No function definition found in the provided code."}

    # Sử dụng test_cases_dicts đã chuyển đổi
    for i, test_case in enumerate(test_cases_dicts):
        input_val = test_case.get("input")
        expected_output = test_case.get("expected_output")
        actual_output = None
        passed = False
        error = None

        try:
            if isinstance(input_val, (list, tuple)):
                # Unpack if multiple arguments
                actual_output = target_function(*input_val)
            else:
                actual_output = target_function(input_val)  # Single argument

            passed = (actual_output == expected_output)
        except Exception as e:
            error = str(e)
            passed = False

        if not passed:
            overall_success = False

        results.append({
            "test_case": test_case,
            "passed": passed,
            "actual_output": actual_output,
            "error": error
        })
        print(
            f"Test Case {i + 1}: Input={input_val}, Expected={expected_output}, Actual={actual_output}, Passed={passed}")

    print(
        f"--- Code Execution Finished. Overall Success: {overall_success} ---\n")
    return {"success": overall_success, "results": results}


request_analyzer = Agent(
    name="RequestAnalyzer",
    model=model,
    role="Phân tích yêu cầu người dùng và tạo ra yêu cầu chi tiết cho việc lập trình và kiểm thử.",
    instructions=[
        "Với một yêu cầu tổng quát từ người dùng, hãy phân tích kỹ lưỡng.",
        "Chia yêu cầu thành hai phần rõ ràng, chi tiết:",
        "1.  `code_requirement`: Mô tả chính xác những gì hàm hoặc đoạn mã cần làm, bao gồm đầu vào, đầu ra và bất kỳ ràng buộc nào.",
        "2.  `test_requirement`: Mô tả các LOẠI trường hợp kiểm thử cần được tạo ra để xác minh tính đúng đắn của mã. Tuyệt đối không sinh ra các giá trị đầu vào hoặc đầu ra cụ thể, chỉ tập trung vào các kịch bản kiểm thử (ví dụ: trường hợp biên, trường hợp hợp lệ, trường hợp không hợp lệ, trường hợp đặc biệt, trường hợp ngoại lệ). Đảm bảo rằng mô tả này đủ chi tiết để một agent khác có thể từ đó sinh ra các test cases cụ thể.",
        "Kết quả cuối cùng phải là một đối tượng JSON hoặc dictionary có hai khóa: `code_requirement` và `test_requirement`.",
        "Ví dụ nếu yêu cầu là 'Viết hàm Python để tính tổng hai số':",
        "{",
        '  "code_requirement": "Viết một hàm Python có tên `add_two_numbers` nhận hai số nguyên (int) làm đối số và trả về tổng của chúng dưới dạng số nguyên.",',
        '  "test_requirement": "Tạo một tập hợp các test cases cho hàm `add_two_numbers`. Bao gồm các trường hợp thông thường (ví dụ: hai số dương, một số âm và một số dương), trường hợp biên (ví dụ: tổng bằng 0, tổng lớn nhất có thể), và các trường hợp không hợp lệ (ví dụ: truyền vào chuỗi hoặc giá trị None). Không bao gồm các giá trị cụ thể trong mô tả này, chỉ mô tả các loại kiểm thử cần thiết."',
        "}",
    ],
    response_model=CodeAndTestRequirements,
)

code_generator = Agent(
    name="CodeGenerator",
    model=model,
    role="Viết mã chương trình dựa trên yêu cầu chi tiết.",
    instructions=[
        "Bạn là một nhà phát triển phần mềm chuyên nghiệp. Với một `code_requirement` và `test_requirement` đã cung cấp, hãy dựa vào hai thông tin trên viết mã Python chất lượng cao.",
        "Mã phải tuân thủ yêu cầu một cách chính xác, rõ ràng, dễ đọc và hiệu quả.",
        "Chỉ trả về đoạn mã Python đã hoàn chỉnh. Không bao gồm bất kỳ giải thích, ví dụ sử dụng hoặc văn bản bổ sung nào khác.",
        "Đảm bảo mã có thể chạy được và không có lỗi cú pháp.",
    ],
    success_criteria= "Trả về một đoạn mã Python hoàn chỉnh, có thể chạy được và tuân thủ chính xác yêu cầu đã cho trong `code_requirement`.",
)

test_generator = Agent(
    name="TestGenerator",
    model=model,
    role="Tạo ra các trường hợp kiểm thử (test cases) dựa trên yêu cầu kiểm thử chi tiết.",
    instructions=[
        "Bạn là một kỹ sư kiểm thử phần mềm chuyên nghiệp. Với một `test_requirement` đã cho, hãy tạo ra một bộ test cases toàn diện.",
        "Mỗi test case phải là một dictionary có hai khóa: `input` và `expected_output`.",
        "Nếu hàm cần kiểm tra nhận nhiều đối số, `input` phải là một tuple chứa các đối số đó.",
        "Đảm bảo rằng các test cases bao gồm các trường hợp thông thường, biên và các trường hợp lỗi tiềm năng (nếu có thể xác định từ yêu cầu).",
        "Trả về một danh sách (list) các test cases đã tạo. Không bao gồm bất kỳ giải thích hoặc văn bản bổ sung nào khác.",
        "Ví dụ nếu yêu cầu là 'Tạo test cases cho hàm `add_two_numbers` nhận hai số nguyên và trả về tổng':",
        "[",
        '  {"input": [2, 3], "expected_output": 5},',
        '  {"input": [-1, 1], "expected_output": 0},',
        '  {"input": [0, 0], "expected_output": 0},',
        '  {"input": [1000, 2000], "expected_output": 3000}',
        "]",
    ],
    success_criteria="Trả về một danh sách các test cases hợp lệ, mỗi test case là một dictionary với các khóa 'input' và 'expected_output'.",
)

# --- Định nghĩa TeamLeader ---

team_leader = Team(
    name="TeamLeader",
    mode="coordinate",  # Cho phép team tự điều phối các agent thành viên
    model=model,
    members=[request_analyzer, code_generator, test_generator],
    description="Bạn là người quản lý dự án và điều phối toàn bộ quá trình phát triển phần mềm.",
    instructions=[
        "Khi nhận được một yêu cầu từ người dùng, nhiệm vụ của bạn là điều phối các agent thành viên để tạo ra mã chất lượng cao, được kiểm thử kỹ lưỡng.",
        "**Bước 1: Phân tích yêu cầu.**",
        "  - Đầu tiên, gửi yêu cầu của người dùng tới `RequestAnalyzer` để nhận về `code_requirement` và `test_requirement`.",
        "  - Đảm bảo rằng kết quả nhận được từ `RequestAnalyzer` là một đối tượng JSON hoặc dictionary hợp lệ với hai khóa này.",
        "**Bước 2: Giao việc song song.**",
        "  - Sau khi có `code_requirement` và `test_requirement`, hãy gửi `code_requirement` cho `CodeGenerator` và `test_requirement` cho `TestGenerator` *một cách đồng thời* (bạn có thể gọi cả hai agent trong cùng một turn nếu cần hoặc dựa vào `mode='coordinate'` để hệ thống tự tối ưu).",
        "  - Chờ đợi kết quả từ cả hai agent.",
        "**Bước 3: Thực hiện kiểm thử.**",
        "  - Khi bạn đã nhận được mã từ `CodeGenerator` và các test cases từ `TestGenerator` (đảm bảo chúng có định dạng đúng), hãy sử dụng công cụ `run_python_code` để thực thi mã với các test cases.",
        "  - Phân tích kết quả kiểm thử được trả về từ `run_python_code`.",
        "**Bước 4: Lặp lại và tinh chỉnh.**",
        "  - Nếu tất cả các test cases đều vượt qua (passed), hãy thông báo thành công và trả về mã cuối cùng cùng với kết quả kiểm thử.",
        "  - Nếu có bất kỳ test case nào thất bại, hãy cung cấp thông tin chi tiết về các lỗi kiểm thử (failed test cases, actual_output, error) cho `CodeGenerator`.",
        "  - Yêu cầu `CodeGenerator` chỉnh sửa mã dựa trên các lỗi đã báo cáo.",
        "  - Lặp lại Bước 3 và 4 cho đến khi mã vượt qua tất cả các test hoặc đến khi bạn nhận thấy không thể sửa lỗi thêm.",
        "**Bước 5: Hoàn thành.**",
        "  - Khi tất cả test cases đã vượt qua, bạn hãy cung cấp đoạn mã cuối cùng đã kiểm thử thành công cho người dùng.",
    ],
    # Thay đổi ở đây: truyền trực tiếp hàm `run_python_code`
    tools=[run_python_code],
    enable_agentic_context=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
    get_member_information_tool=True
)

print("Bắt đầu quy trình phát triển và kiểm thử...")
team_leader.print_response("Viết một hàm Python có tên `is_palindrome` nhận một chuỗi và trả về True nếu nó là palindrome, ngược lại trả về False. Bỏ qua chữ hoa/thường và khoảng trắng.")

print("Quy trình đã hoàn thành. Bạn có thể tiếp tục với yêu cầu khác hoặc dừng lại.")


