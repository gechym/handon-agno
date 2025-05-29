import os
import openai


from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.litellm import LiteLLM
from agno.reasoning.step import ReasoningSteps
from textwrap import dedent
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
dotenv_path = Path('/home/tran-tien/Documents/PyCharmProject/Work/FTech/Agno/research/.env')
load_dotenv(dotenv_path=dotenv_path)

os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")
os.environ["LITELLM_API_KEY"] = os.getenv("LITELLM_API_KEY")

client = openai.Client(
    base_url="https://litellm.dev.ftech.ai",
    api_key=os.environ["LITELLM_API_KEY"],
)

min_steps, max_steps = 3, 5
reason_agent = Agent(
    model=Gemini(
        id="gemini-2.5-flash-preview-05-20", temperature=0.1
    ),
    response_model=ReasoningSteps,
    instructions=dedent(f"""\
        Bước 1 - Phân tích Vấn đề:
        - Diễn đạt lại rõ ràng nhiệm vụ của người dùng bằng ngôn từ của bạn để đảm bảo hiểu rõ hoàn toàn.
        - Xác định rõ ràng thông tin cần thiết và những công cụ hoặc tài nguyên có thể cần.

        Bước 2 - Phân tách và Lập chiến lược:
        - Chia nhỏ vấn đề thành các nhiệm vụ con được xác định rõ ràng.
        - Phát triển ít nhất hai chiến lược hoặc cách tiếp cận riêng biệt để giải quyết vấn đề nhằm đảm bảo tính toàn diện.

        Bước 3 - Làm rõ Ý định và Lập kế hoạch:
        - Diễn đạt rõ ràng ý định của người dùng đằng sau yêu cầu của họ.
        - Chọn chiến lược phù hợp nhất từ Bước 2, lý giải rõ ràng lựa chọn của bạn dựa trên sự phù hợp với ý định của người dùng và các ràng buộc của nhiệm vụ.
        - Xây dựng một kế hoạch hành động chi tiết từng bước, vạch ra trình tự các hành động cần thiết để giải quyết vấn đề.

        Bước 4 - Thực thi Kế hoạch Hành động:
        Đối với mỗi bước đã lên kế hoạch, hãy ghi lại:
        1.  **Tiêu đề**: Tiêu đề ngắn gọn tóm tắt bước.
        2.  **Hành động**: Nêu rõ hành động tiếp theo của bạn ở ngôi thứ nhất ('Tôi sẽ...').
        3.  **Kết quả**: Thực hiện hành động của bạn bằng các công cụ cần thiết và cung cấp bản tóm tắt ngắn gọn về kết quả.
        4.  **Suy luận**: Giải thích rõ ràng lý do của bạn, bao gồm:
            -   Sự cần thiết: Tại sao hành động này là cần thiết.
            -   Các cân nhắc: Nêu bật các cân nhắc chính, những thách thức tiềm ẩn và chiến lược giảm thiểu.
            -   Tiến trình: Bước này tiếp nối hoặc phát triển hợp lý từ các hành động trước đó như thế nào.
            -   Giả định: Nêu rõ bất kỳ giả định nào được đưa ra và lý giải tính hợp lệ của chúng.
        5.  **Hành động Tiếp theo**: Chọn rõ ràng bước tiếp theo của bạn từ:
            -   **tiếp tục**: Nếu cần các bước tiếp theo.
            -   **xác thực**: Khi bạn đạt được một câu trả lời tiềm năng, báo hiệu rằng nó đã sẵn sàng để xác thực.
            -   **câu trả lời cuối cùng**: Chỉ khi bạn đã tự tin xác thực giải pháp.
            -   **đặt lại**: Ngay lập tức khởi động lại phân tích nếu phát hiện lỗi nghiêm trọng hoặc kết quả không chính xác.
        6.  **Điểm Tự tin**: Cung cấp điểm tự tin bằng số (0.0–1.0) cho biết mức độ chắc chắn của bạn về tính đúng đắn của bước và kết quả của nó.

        Bước 5 - Xác thực (bắt buộc trước khi chốt câu trả lời):
        - Xác thực rõ ràng giải pháp của bạn bằng cách:
            -   Đối chiếu với các cách tiếp cận thay thế (được phát triển ở Bước 2).
            -   Sử dụng các công cụ hoặc phương pháp bổ sung có sẵn để độc lập xác nhận độ chính xác.
        - Ghi lại rõ ràng kết quả xác thực và lý do đằng sau phương pháp xác thực đã chọn.
        - Nếu xác thực thất bại hoặc phát sinh sai lệch, hãy xác định rõ ràng lỗi, đặt lại phân tích của bạn và điều chỉnh kế hoạch cho phù hợp.

        Bước 6 - Cung cấp Câu trả lời Cuối cùng:
        - Sau khi đã xác thực kỹ lưỡng và tự tin, hãy trình bày giải pháp của bạn một cách rõ ràng và súc tích.
        - Tóm tắt ngắn gọn cách câu trả lời của bạn giải quyết ý định ban đầu của người dùng và hoàn thành nhiệm vụ đã nêu.

        Hướng dẫn Vận hành Chung:
        - Đảm bảo phân tích của bạn luôn:
            -   **Hoàn chỉnh**: Giải quyết tất cả các yếu tố của nhiệm vụ.
            -   **Toàn diện**: Khám phá các góc nhìn đa dạng và dự đoán các kết quả tiềm năng.
            -   **Hợp lý**: Duy trì sự mạch lạc giữa tất cả các bước.
            -   **Có thể thực hiện**: Trình bày các bước và hành động có thể triển khai rõ ràng.
            -   **Sâu sắc**: Đưa ra những góc nhìn đổi mới và độc đáo nếu có thể.
        - Luôn xử lý rõ ràng các lỗi và sai sót bằng cách đặt lại hoặc sửa đổi các bước ngay lập tức.
        - Tuân thủ nghiêm ngặt tối thiểu {min_steps} và tối đa {max_steps} bước để đảm bảo giải quyết nhiệm vụ hiệu quả.
        - Thực thi các công cụ cần thiết một cách chủ động và không do dự, ghi lại rõ ràng việc sử dụng công cụ.
        - Chỉ tạo một thể hiện (instance) duy nhất của ReasoningSteps cho phản hồi của bạn.\
        """),
        debug_mode=True,
)

normal_agent = Agent(
    model=LiteLLM(
        id="vplay-va-gpt-4o-2024-11-20",
        client=client,
    ),
    reasoning=True,
    reasoning_agent=reason_agent,
    debug_mode=True,
)
# reasoning_model.print_response("9.11 and 9.9 -- which is bigger?")
normal_agent.print_response("9.11 và 9.9 -- cái nào lớn hơn?", show_full_reasoning=True)
