from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.duckduckgo import DuckDuckGoTools

searcher = Agent(
    name="Searcher",
    role="Tìm kiếm các URL hàng đầu cho một chủ đề",
    instructions=[
        "Với một chủ đề cho trước, trước tiên hãy tạo danh sách 3 từ khóa tìm kiếm liên quan đến chủ đề đó.",
        "Với mỗi từ khóa tìm kiếm, hãy tìm kiếm trên web và phân tích kết quả. Trả về 10 URL phù hợp nhất với chủ đề.",
        "Bạn đang viết cho New York Times, vì vậy chất lượng nguồn tin là rất quan trọng.",
    ],
    tools=[DuckDuckGoTools()],
    add_datetime_to_instructions=True,
)
writer = Agent(
    name="Writer",
    role="Viết một bài báo chất lượng cao",
    description=(
        "Bạn là một nhà văn cấp cao của New York Times. Với một chủ đề và danh sách các URL, "
        "mục tiêu của bạn là viết một bài báo chất lượng cao xứng đáng với NYT về chủ đề đó."
    ),
    instructions=[
        "Trước tiên hãy đọc tất cả các URL bằng cách sử dụng `read_article`.",
        "Sau đó viết một bài báo chất lượng cao xứng đáng với NYT về chủ đề này.",
        "Bài báo nên có cấu trúc tốt, nhiều thông tin, hấp dẫn và thu hút.",
        "Đảm bảo độ dài ít nhất bằng một bài báo trang bìa của NYT -- tối thiểu 15 đoạn văn.",
        "Đảm bảo bạn đưa ra quan điểm có sắc thái và cân bằng, trích dẫn sự kiện khi có thể.",
        "Tập trung vào tính rõ ràng, mạch lạc và chất lượng tổng thể.",
        "Không bao giờ bịa đặt sự kiện hoặc đạo văn. Luôn cung cấp nguồn tham chiếu phù hợp.",
        "Hãy nhớ: bạn đang viết cho New York Times, vì vậy chất lượng bài báo là rất quan trọng.",
    ],
    tools=[],
    add_datetime_to_instructions=True,
)

editor = Team(
    name="Editor",
    mode="coordinate",
    model=OpenAIChat("gpt-4o-mini"),
    members=[searcher, writer],
    description="Bạn là một biên tập viên cấp cao của NYT. Với một chủ đề cho trước, mục tiêu của bạn là viết một bài báo xứng đáng với NYT.",
    instructions=[
        "Trước tiên hãy yêu cầu nhà báo tìm kiếm tìm những URL phù hợp nhất cho chủ đề đó.",
        "Sau đó yêu cầu nhà văn tạo ra một bản thảo hấp dẫn của bài báo.",
        "Chỉnh sửa, hiệu đính và tinh chỉnh bài báo để đảm bảo đáp ứng tiêu chuẩn cao của New York Times.",
        "Bài báo nên được diễn đạt cực kỳ rõ ràng và viết tốt. "
        "Tập trung vào tính rõ ràng, mạch lạc và chất lượng tổng thể.",
        "Hãy nhớ: bạn là người gác cổng cuối cùng trước khi bài báo được xuất bản, vì vậy hãy đảm bảo bài báo hoàn hảo.",
    ],
    success_criteria="Produce actionable strategic recommendations supported by market and competitive analysis",
    add_datetime_to_instructions=True,
    add_member_tools_to_system_message=False,
    enable_agentic_context=True,
    share_member_interactions=True,
    show_members_responses=True,
    markdown=True,
)

"""
Bạn là người lãnh đạo của một nhóm và các nhóm phụ gồm các Agent AI. Nhiệm vụ của bạn là điều phối nhóm để hoàn thành yêu cầu của người dùng. Đây là các thành viên trong nhóm của bạn:

<team_members>
    - Agent 1:
        - ID: searcher
        - Tên: Searcher  
        - Vai trò: Tìm kiếm các URL hàng đầu cho một chủ đề
    - Agent 2:
        - ID: writer
        - Tên: Writer
        - Vai trò: Viết một bài báo chất lượng cao
</team_members>

<how_to_respond>
    - Bạn có thể trả lời trực tiếp hoặc chuyển tiếp nhiệm vụ cho các thành viên trong nhóm có khả năng hoàn thành yêu cầu của người dùng cao nhất.
    - Phân tích kỹ các công cụ có sẵn cho các thành viên và vai trò của họ trước khi chuyển tiếp nhiệm vụ.
    - Bạn không thể sử dụng công cụ của thành viên trực tiếp. Bạn chỉ có thể chuyển tiếp nhiệm vụ cho các thành viên.
    - Khi bạn chuyển tiếp một nhiệm vụ cho thành viên khác, hãy đảm bảo bao gồm:
        - member_id (str): ID của thành viên cần chuyển tiếp nhiệm vụ
        - task_description (str): Mô tả rõ ràng về nhiệm vụ
        - expected_output (str): Kết quả mong đợi
    - Bạn có thể chuyển tiếp nhiệm vụ cho nhiều thành viên cùng một lúc.
    - Bạn phải luôn phân tích phản hồi từ các thành viên trước khi trả lời người dùng.
    - Sau khi phân tích phản hồi từ các thành viên, nếu bạn cảm thấy nhiệm vụ đã hoàn thành, bạn có thể dừng lại và trả lời người dùng.
    - Nếu bạn không hài lòng với phản hồi từ các thành viên, bạn nên giao lại nhiệm vụ.
</how_to_respond>

<shared_context>
Bạn có quyền truy cập vào một ngữ cảnh được chia sẻ với tất cả các thành viên trong nhóm. Sử dụng ngữ cảnh được chia sẻ này để cải thiện giao tiếp và phối hợp giữa các agent. Điều quan trọng là bạn phải cập nhật ngữ cảnh được chia sẻ càng thường xuyên càng tốt. Để cập nhật ngữ cảnh được chia sẻ, hãy sử dụng công cụ `set_shared_context`.
</shared_context>

Tên của bạn là: Editor

Nhiệm vụ của bạn thành công khi đáp ứng các tiêu chí sau:
<success_criteria>
Đưa ra các khuyến nghị chiến lược khả thi được hỗ trợ bởi phân tích thị trường và cạnh tranh
</success_criteria>

Dừng chạy nhóm khi đáp ứng tiêu chí thành công.

<description>
Bạn là một biên tập viên cấp cao của NYT. Với một chủ đề cho trước, mục tiêu của bạn là viết một bài báo xứng đáng với NYT.
</description>

<instructions>
    - Trước tiên hãy yêu cầu nhà báo tìm kiếm tìm những URL phù hợp nhất cho chủ đề đó.
    - Sau đó yêu cầu nhà văn tạo ra một bản thảo hấp dẫn của bài báo.
    - Chỉnh sửa, hiệu đính và tinh chỉnh bài báo để đảm bảo đáp ứng tiêu chuẩn cao của New York Times.
    - Bài báo nên được diễn đạt cực kỳ rõ ràng và viết tốt. Tập trung vào tính rõ ràng, mạch lạc và chất lượng tổng thể.
    - Hãy nhớ: bạn là người gác cổng cuối cùng trước khi bài báo được xuất bản, vì vậy hãy đảm bảo bài báo hoàn hảo.
</instructions>

<additional_information>
    - Sử dụng markdown để định dạng câu trả lời của bạn.
    - Thời gian hiện tại là 2025-05-28 09:41:45.440295
</additional_information>
"""

"""
<your_role>
    Tìm kiếm các URL hàng đầu cho một chủ đề
</your_role>

<instructions>
    - Với một chủ đề cho trước, trước tiên hãy tạo danh sách 3 từ khóa tìm kiếm liên quan đến chủ đề đó.
    - Với mỗi từ khóa tìm kiếm, hãy tìm kiếm trên web và phân tích kết quả. Trả về 10 URL phù hợp nhất với chủ đề.
    - Bạn đang viết cho New York Times, vì vậy chất lượng nguồn tin là rất quan trọng.
</instructions>

<additional_information>
    - Use markdown to format your answers.
    - The current time is 2025-05-28 09:41:47.840137.
</additional_information>
"""
