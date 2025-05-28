
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from dotenv import load_dotenv

load_dotenv()

english_agent = Agent(
    name="English Agent",
    role="You can only answer in English",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You must only respond in English",
    ],
)

japanese_agent = Agent(
    name="Japanese Agent",
    role="You can only answer in Japanese",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You must only respond in Japanese",
    ],
)
chinese_agent = Agent(
    name="Chinese Agent",
    role="You can only answer in Chinese",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You must only respond in Chinese",
    ],
)
spanish_agent = Agent(
    name="Spanish Agent",
    role="You can only answer in Spanish",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You must only respond in Spanish",
    ],
)

french_agent = Agent(
    name="French Agent",
    role="You can only answer in French",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You must only respond in French",
    ],
)

german_agent = Agent(
    name="German Agent",
    role="You can only answer in German",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "You must only respond in German",
    ],
)
multi_language_team = Team(
    name="Multi Language Team",
    mode="route",
    model=OpenAIChat(id="gpt-4o-mini"),
    members=[
        english_agent,
        spanish_agent,
        japanese_agent,
        french_agent,
        german_agent,
        chinese_agent,
    ],
    show_tool_calls=True,
    markdown=True,
    instructions=[
        "You are a language router that directs questions to the appropriate language agent.",
        "If the user asks in a language whose agent is not a team member, respond in English with:",
        "'I can only answer in the following languages: English, Spanish, Japanese, French and German.",
        "Please ask your question in one of these languages.'",
        "Always check the language of the user's input before routing to an agent.",
        "For unsupported languages like Italian, respond in English with the above message.",
    ],
    show_members_responses=True,
)

"""
Bạn là người lãnh đạo của một nhóm và các nhóm phụ gồm các Agent AI. Nhiệm vụ của bạn là điều phối nhóm để hoàn thành yêu cầu của người dùng. Đây là các thành viên trong nhóm của bạn:
<team_members>
    - Agent 1: - ID: english-agent - Tên: English Agent - Vai trò: Chỉ có thể trả lời bằng tiếng Anh
    - Agent 2: - ID: spanish-agent - Tên: Spanish Agent - Vai trò: Chỉ có thể trả lời bằng tiếng Tây Ban Nha
    - Agent 3: - ID: japanese-agent - Tên: Japanese Agent - Vai trò: Chỉ có thể trả lời bằng tiếng Nhật
    - Agent 4: - ID: french-agent - Tên: French Agent - Vai trò: Chỉ có thể trả lời bằng tiếng Pháp
    - Agent 5: - ID: german-agent - Tên: German Agent - Vai trò: Chỉ có thể trả lời bằng tiếng Đức
    - Agent 6: - ID: chinese-agent - Tên: Chinese Agent - Vai trò: Chỉ có thể trả lời bằng tiếng Trung
</team_members>
<how_to_respond>
- Bạn có thể trả lời trực tiếp hoặc chuyển tiếp nhiệm vụ cho các thành viên trong nhóm có khả năng hoàn thành yêu cầu của người dùng cao nhất.
- Phân tích kỹ các công cụ có sẵn cho các thành viên và vai trò của họ trước khi chuyển tiếp nhiệm vụ.
- Khi bạn chuyển tiếp một nhiệm vụ cho Agent khác, hãy đảm bảo bao gồm:
- member_id (str): ID của thành viên cần chuyển tiếp nhiệm vụ.
- expected_output (str): Kết quả mong đợi.
- Bạn có thể chuyển tiếp nhiệm vụ cho nhiều thành viên cùng một lúc.
</how_to_respond>

Tên của bạn là: Multi Language Team

<instructions>
    - Bạn là một bộ định tuyến ngôn ngữ điều hướng câu hỏi đến agent ngôn ngữ thích hợp.
    - Nếu người dùng hỏi bằng ngôn ngữ mà agent không phải là thành viên trong nhóm, hãy trả lời bằng tiếng Anh với:
    - 'Tôi chỉ có thể trả lời bằng các ngôn ngữ sau: Tiếng Anh, Tây Ban Nha, Nhật, Pháp và Đức.
    - Vui lòng đặt câu hỏi bằng một trong những ngôn ngữ này.'
    - Luôn kiểm tra ngôn ngữ đầu vào của người dùng trước khi chuyển đến một agent.
    - Đối với các ngôn ngữ không được hỗ trợ như tiếng Ý, hãy trả lời bằng tiếng Anh với thông báo trên.
</instructions>
<additional_information>
    - Sử dụng markdown để định dạng câu trả lời của bạn.
</additional_information>
"""
