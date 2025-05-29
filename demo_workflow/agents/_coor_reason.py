import re
from textwrap import dedent
from typing import Any

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.reasoning.step import ReasoningSteps
from agno.team.team import Team
from dotenv import load_dotenv
from pydantic import BaseModel, Field

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
    input: Any = Field(description="Giá trị đầu vào cho hàm. Có thể là một giá trị đơn hoặc một list/tuple nếu hàm nhận nhiều đối số.")
    expected_output: Any = Field(description="Giá trị đầu ra mong đợi từ hàm.")


# ReasoningSteps, ReasoningStep, NextAction đã được giả định là import từ agno.reasoning.step

# --- Tool run_python_code (Đã sửa lỗi type hint cho test_cases) ---
def run_python_code(code: str, test_cases: list[TestCaseItem]) -> dict:  # Đã sửa từ 'list' sang 'List[TestCaseItem]'
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
    test_cases_dicts = [tc.model_dump() if isinstance(tc, BaseModel) else tc for tc in test_cases]
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

    for i, test_case in enumerate(test_cases_dicts):  # Sử dụng test_cases_dicts đã chuyển đổi
        input_val = test_case.get("input")
        expected_output = test_case.get("expected_output")
        actual_output = None
        passed = False
        error = None

        try:
            if isinstance(input_val, (list, tuple)):
                actual_output = target_function(*input_val)  # Unpack if multiple arguments
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
        print(f"Test Case {i + 1}: Input={input_val}, Expected={expected_output}, Actual={actual_output}, Passed={passed}")

    print(f"--- Code Execution Finished. Overall Success: {overall_success} ---\n")
    return {"success": overall_success, "results": results}


# --- Định nghĩa Agent reason_request_analyzer (Đã tối ưu prompt) ---
# Agent này CHỈ làm nhiệm vụ phân tích, suy nghĩ, đưa ra nhận định, hướng.
min_reasoning_steps = 3  # Đặt giá trị mặc định, có thể thay đổi
max_reasoning_steps = 5  # Đặt giá trị mặc định, có thể thay đổi

reason_request_analyzer = Agent(
    name="ReasonRequestAnalyzer",
    model=model,
    response_model=ReasoningSteps,  # Trả về chuỗi các bước suy luận
    role="Thực hiện quá trình phân tích và suy luận chi tiết để định hướng xây dựng **yêu cầu đoạn code** và **mô tả các loại kiểm thử ** cần thiết.",
    instructions=dedent(f"""\
        Bạn là một chuyên gia phân tích yêu cầu cao cấp. Nhiệm vụ của bạn là nhận một yêu cầu tổng quát từ người dùng và thực hiện quá trình suy luận chi tiết từng bước.
        Mục tiêu cuối cùng của quá trình suy luận của bạn là cung cấp đủ thông tin phân tích để một agent khác (RequestAnalyzer) có thể tự tổng hợp `code_requirement` và `test_requirement`.
        Bạn KHÔNG TỰ TỔNG HỢP chuỗi `Code_Requirement: ... \n Test_Requirement: ...` cuối cùng. Thay vào đó, bạn sẽ đưa ra các thành phần phân tích và hướng dẫn cần thiết trong các bước suy luận của mình.
        Bạn PHẢI trả về toàn bộ quá trình suy luận của mình dưới dạng một đối tượng `ReasoningSteps`.

        --- Hướng dẫn Reasoning chi tiết của bạn ---

        Bạn phải tạo MỘT `ReasoningStep` cho mỗi bước dưới đây.

        **Bước 1 - Phân tích Vấn đề:**
        - **Hành động**: Tôi sẽ diễn đạt lại rõ ràng nhiệm vụ của người dùng bằng ngôn từ của tôi để đảm bảo hiểu rõ hoàn toàn. Tôi sẽ xác định rõ ràng thông tin cần thiết và những yếu tố chức năng chính, các ràng buộc và điều kiện biên được nêu trong yêu cầu gốc.
        - **Kết quả**: [Hãy mô tả kết quả của việc phân tích vấn đề ở đây. Ví dụ: "Yêu cầu người dùng: 'Viết hàm Python có tên `is_palindrome` nhận một chuỗi và trả về True nếu nó là palindrome, ngược lại trả về False. Bỏ qua chữ hoa/thường và khoảng trắng.' Các yếu tố chính cần phân tích: tên hàm, đầu vào (kiểu dữ liệu), đầu ra (kiểu dữ liệu), logic cốt lõi, và các ràng buộc (chuẩn hóa chuỗi)."]
        - **Suy luận**: [Giải thích lý do, cân nhắc, tiến trình và giả định.]
        - **Hành động Tiếp theo**: `NextAction.CONTINUE`
        - **Điểm Tự tin**: [Điểm số (0.0-1.0)]

        **Bước 2 - Phân tách và Lập chiến lược:**
        - **Hành động**: Tôi sẽ chia nhỏ vấn đề thành hai lĩnh vực chính: định nghĩa các thành phần cho `code_requirement` và định nghĩa các thành phần cho `test_requirement` (chỉ mô tả các loại test). Tôi sẽ phát triển ít nhất hai chiến lược hoặc cách tiếp cận riêng biệt cho mỗi lĩnh vực để đảm bảo tính toàn diện trong việc định nghĩa các tiêu chí.
        - **Kết quả**: [Mô tả các lĩnh vực chính và các chiến lược được xem xét. Ví dụ: "Lĩnh vực 1 (Code): Xác định signature hàm, mô tả logic cốt lõi. Lĩnh vực 2 (Test): Chiến lược bao phủ test (chức năng, biên, lỗi), định dạng đầu vào/đầu ra test. Chiến lược cho Code: từ API đến logic. Chiến lược cho Test: bao phủ tích cực các trường hợp."]
        - **Suy luận**: [Giải thích lý do, cân nhắc, tiến trình và giả định.]
        - **Hành động Tiếp theo**: `NextAction.CONTINUE`
        - **Điểm Tự tin**: [Điểm số]

        **Bước 3 - Làm rõ Ý định và Lập kế hoạch:**
        - **Hành động**: Tôi sẽ diễn đạt rõ ràng ý định của người dùng và chọn chiến lược phù hợp nhất từ Bước 2 cho từng lĩnh vực, lý giải lựa chọn. Sau đó, tôi sẽ xây dựng một kế hoạch hành động chi tiết từng bước để tạo ra các thành phần cần thiết cho `code_requirement` và `test_requirement`.
        - **Kết quả**: [Mô tả ý định, chiến lược đã chọn và kế hoạch hành động chi tiết. Ví dụ: "Ý định: người dùng muốn một hàm đáng tin cậy và được kiểm thử kỹ lưỡng. Kế hoạch: (1) Xác định chi tiết tên hàm, tham số, kiểu trả về và mô tả logic cho `code_requirement`. (2) Phân loại các nhóm test case cần thiết và định dạng input/output cho `test_requirement`. (3) Tổng hợp các phân tích."]
        - **Suy luận**: [Giải thích lý do, cân nhắc, tiến trình và giả định.]
        - **Hành động Tiếp theo**: `NextAction.CONTINUE`
        - **Điểm Tự tin**: [Điểm số]

        **Bước 4 - Thực thi Kế hoạch Hành động (Nội bộ):**
        Đây là bước nơi bạn thực hiện các hành động nội bộ để xây dựng các thành phần của `code_requirement` và `test_requirement`. Bạn PHẢI tạo MỘT `ReasoningStep` riêng biệt cho MỖI hành động nhỏ bạn thực hiện trong kế hoạch của mình.
        
        **Lưu ý:** Khi bạn đã hoàn thành việc tạo ra các thành phần phân tích cho cả `code_requirement` và `test_requirement`, bước tiếp theo của bạn là `NextAction.VALIDATE`.

        **Bước 5 - Xác thực (bắt buộc trước khi chốt câu trả lời):**
        - **Hành động**: Tôi sẽ xác thực rõ ràng các thành phần phân tích đã tạo ra bằng cách đối chiếu với các cách tiếp cận thay thế và kiểm tra tính đầy đủ, rõ ràng của từng thành phần. Tôi sẽ đảm bảo `test_requirement` KHÔNG CÓ GIÁ TRỊ CỤ THỂ, chỉ mô tả loại test.
        - **Kết quả**: [Mô tả kết quả xác thực. Ví dụ: "Tất cả các thành phần phân tích cho `code_requirement` và `test_requirement` đều đáp ứng đủ tiêu chí: chi tiết, rõ ràng, và `test_requirement` chỉ mô tả loại test."]
        - **Suy luận**: [Giải thích lý do, cân nhắc, tiến trình và giả định.]
        - **Hành động Tiếp theo**: `NextAction.FINAL_ANSWER` (nếu xác thực thành công) hoặc `NextAction.RESET` (nếu có lỗi).
        - **Điểm Tự tin**: [Điểm số]

        **Bước 6 - Cung cấp Câu trả lời Cuối cùng (Tổng hợp phân tích cho RequestAnalyzer):**
        - **Hành động**: Tôi sẽ tổng hợp các phân tích quan trọng từ các bước trước đó, đặc biệt là từ Bước 4 và 5, để đưa ra một bản tóm tắt mạch lạc về các thành phần của `code_requirement` và `test_requirement` mà RequestAnalyzer có thể sử dụng để xây dựng kết quả cuối cùng.
        - **Kết quả**: [Đây là nơi bạn cung cấp TẤT CẢ các thông tin cần thiết mà RequestAnalyzer sẽ dùng để tổng hợp thành `CodeAndTestRequirements`. Ví dụ: "Phân tích Code_Requirement: Tên hàm: is_palindrome; Đầu vào: chuỗi (str); Đầu ra: boolean; Logic chính: Kiểm tra tính đối xứng của chuỗi sau khi chuẩn hóa (loại bỏ khoảng trắng và chuyển chữ hoa/thường thành chữ thường). Phân tích Test_Requirement: Chiến lược kiểm thử: Bao phủ chức năng cơ bản, trường hợp biên, và các điều kiện đặc biệt. Các loại test case cần thiết: Test chuỗi palindrome điển hình, test chuỗi không palindrome, test với chuỗi rỗng, test với chuỗi một ký tự, test với chuỗi chứa khoảng trắng và chữ hoa/thường. Định dạng test case mong đợi: 'input' là chuỗi, 'expected_output' là boolean."]
        - **Suy luận**: [Tóm tắt ngắn gọn cách các phân tích này giải quyết ý định ban đầu của người dùng và hoàn thành nhiệm vụ.]
        - **Hành động Tiếp theo**: `NextAction.FINAL_ANSWER`
        - **Điểm Tự tin**: 1.0

        Hướng dẫn Vận hành Chung:
        - Đảm bảo phân tích của bạn luôn: Hoàn chỉnh, Toàn diện, Hợp lý, Có thể thực hiện, Sâu sắc.
        - Luôn xử lý rõ ràng các lỗi và sai sót bằng cách tạo một `ReasoningStep` với `next_action` là `NextAction.RESET` và mô tả lỗi.
        - Tuân thủ nghiêm ngặt tối thiểu {min_reasoning_steps} và tối đa {max_reasoning_steps} bước để đảm bảo giải quyết nhiệm vụ hiệu quả.
        - Chỉ tạo một thể hiện (instance) duy nhất của `ReasoningSteps` cho phản hồi của bạn, chứa TẤT CẢ các bước từ đầu đến cuối.
    """),
    debug_mode=True,
)

# --- Định nghĩa Agent request_analyzer (Đã sửa đổi Prompt) ---
# Agent này sẽ đọc ReasoningSteps và tự tổng hợp Code_Requirement và Test_Requirement.
request_analyzer = Agent(
    name="RequestAnalyzer",
    model=model,
    role="Phân tích yêu cầu người dùng và tạo ra yêu cầu chi tiết cho việc lập trình và kiểm thử.",
    instructions=dedent("""\
        Với một yêu cầu tổng quát từ người dùng, nhiệm vụ của bạn là gọi `reasoning_agent` (`ReasonRequestAnalyzer`) để thực hiện phân tích chi tiết.
        
        Sau khi nhận được kết quả `ReasoningSteps` từ `reasoning_agent`, bạn phải:
        1.  Tìm `ReasoningStep` cuối cùng trong danh sách `reasoning_steps` (bước mà có `next_action` là `NextAction.FINAL_ANSWER`).
        2.  Từ phần `result` của bước cuối cùng đó, hãy **đọc và hiểu** các thông tin phân tích về `code_requirement` và `test_requirement`. Các thông tin này sẽ được trình bày dưới dạng văn bản mô tả các thành phần (ví dụ: "Tên hàm: ...", "Logic chính: ...", "Các loại test case cần thiết: ...").
        3.  Dựa vào các thông tin đã đọc và hiểu, **hãy tự mình tổng hợp và xây dựng** chuỗi `code_requirement` và `test_requirement` hoàn chỉnh theo định dạng mong muốn.
        4.  Sử dụng các chuỗi đã xây dựng để tạo một đối tượng `CodeAndTestRequirements` và trả về nó.
        
        Hãy đảm bảo rằng `test_requirement` của bạn CHỈ MÔ TẢ CÁC LOẠI test, không chứa giá trị cụ thể.
        Nếu không thể tìm thấy bước cuối cùng hoặc không thể trích xuất/xây dựng thông tin cần thiết, hãy báo lỗi.
        
        Ví dụ nếu yêu cầu là 'Viết hàm Python để tính tổng hai số', và bạn nhận được phân tích từ `reasoning_agent`, bạn sẽ tự tổng hợp và trả về JSON sau:
        ```json
        {
          "code_requirement": "Viết một hàm Python có tên `add_two_numbers` nhận hai số nguyên (int) làm đối số và trả về tổng của chúng dưới dạng số nguyên.",
          "test_requirement": "Tạo một tập hợp các test cases cho hàm `add_two_numbers`. Các loại test case cần bao gồm: test chức năng cơ bản (số dương), test với số âm, test với số 0, và test biên (số lớn/nhỏ). Định dạng của mỗi test case phải là một đối tượng chứa 'input' (tuple của hai số nguyên) và 'expected_output' (số nguyên)."
        }
        ```
        Bạn không cần phải tự thực hiện quá trình reasoning. Bạn chỉ tập trung vào việc đọc phân tích của `reasoning_agent` và tự tổng hợp/định dạng lại đầu ra cuối cùng dưới dạng `CodeAndTestRequirements`.
    """),
    reasoning=True,
    reasoning_agent=reason_request_analyzer,  # Gán agent reasoning vào đây!
    # response_model của request_analyzer là CodeAndTestRequirements
    response_model=CodeAndTestRequirements,
    debug_mode=True,
)

# --- Định nghĩa Agent code_generator (Giữ nguyên) ---
code_generator = Agent(
    name="CodeGenerator",
    model=model,
    role="Viết mã chương trình dựa trên yêu cầu chi tiết.",
    instructions=[
        "Bạn là một nhà phát triển phần mềm chuyên nghiệp. Với một `code_requirement` đã cho, hãy viết mã Python chất lượng cao.",
        "Mã phải tuân thủ yêu cầu một cách chính xác, rõ ràng, dễ đọc và hiệu quả.",
        "Chỉ trả về đoạn mã Python đã hoàn chỉnh. Không bao gồm bất kỳ giải thích, ví dụ sử dụng hoặc văn bản bổ sung nào khác.",
        "Đảm bảo mã có thể chạy được và không có lỗi cú pháp.",
    ],
)

# --- Định nghĩa Agent test_generator (Giữ nguyên) ---
test_generator = Agent(
    name="TestGenerator",
    model=model,
    role="Tạo ra các trường hợp kiểm thử (test cases) dựa trên yêu cầu chi tiết.",
    instructions=[
        "Bạn là một kỹ sư kiểm thử phần mềm chuyên nghiệp. Với một `test_requirement` đã cho (chỉ mô tả các LOẠI test), hãy tạo ra một bộ test cases toàn diện với CÁC GIÁ TRỊ CỤ THỂ.",
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
)

# --- Định nghĩa TeamLeader (Đã bỏ comment các bước kiểm thử) ---
team_leader = Team(
    name="TeamLeader",
    mode="coordinate",
    model=model,
    members=[request_analyzer, code_generator, test_generator],
    description="Bạn là người quản lý dự án và điều phối toàn bộ quá trình phát triển phần mềm.",
    instructions=[
        "Khi nhận được một yêu cầu từ người dùng, nhiệm vụ của bạn là điều phối các agent thành viên để tạo ra mã chất lượng cao, được kiểm thử kỹ lưỡng.",
        "**Bước 1: Phân tích yêu cầu.**",
        "  - Đầu tiên, gửi yêu cầu của người dùng tới `RequestAnalyzer` để nhận về một đối tượng JSON chứa `code_requirement` và `test_requirement`.",
        "  - Đảm bảo rằng kết quả nhận được từ `RequestAnalyzer` là một đối tượng JSON hợp lệ với hai khóa này.",
        "**Bước 2: Giao việc song song.**",
        "  - Sau khi có `code_requirement` và `test_requirement` từ `RequestAnalyzer`, hãy gửi `code_requirement` cho `CodeGenerator` và `test_requirement` cho `TestGenerator` *một cách đồng thời*.",
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
        "  - Khi tất cả test cases đã vượt qua, in ra mã Python cuối cùng và xác nhận rằng nó hoạt động chính xác.",
    ],
    tools=[run_python_code],
    add_datetime_to_instructions=True,
    enable_agentic_context=True,
    markdown=True,
    debug_mode=True,
    show_members_responses=True,
    get_member_information_tool=True
)


# --- Thực thi quy trình ---
# while True:
print("Bắt đầu quy trình phát triển và kiểm thử...")
team_leader.print_response("Viết một hàm Python có tên `is_palindrome` nhận một chuỗi và trả về True nếu nó là palindrome, ngược lại trả về False. Bỏ qua chữ hoa/thường và khoảng trắng.")

print("Quy trình đã hoàn thành. Bạn có thể tiếp tục với yêu cầu khác hoặc dừng lại.")
# cont = input("Bạn có muốn tiếp tục với yêu cầu khác không? (y/n): ")
    # if cont.lower() != 'y':
    #     print("Kết thúc quy trình.")
    #     breakc
