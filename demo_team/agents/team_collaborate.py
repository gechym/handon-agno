from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.arxiv import ArxivTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.googlesearch import GoogleSearchTools
from agno.tools.hackernews import HackerNewsTools

reddit_researcher = Agent(
    name="Nghiên cứu viên Reddit",
    role="Nghiên cứu một chủ đề trên Reddit",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGoTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    Bạn là một nghiên cứu viên Reddit.
    Bạn sẽ được cho một chủ đề để nghiên cứu trên Reddit.
    Bạn sẽ cần tìm các bài đăng có liên quan nhất trên Reddit.
    """),
)

hackernews_researcher = Agent(
    name="Nghiên cứu viên HackerNews",
    model=OpenAIChat("gpt-4o-mini"),
    role="Nghiên cứu một chủ đề trên HackerNews.",
    tools=[HackerNewsTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    Bạn là một nghiên cứu viên HackerNews.
    Bạn sẽ được cho một chủ đề để nghiên cứu trên HackerNews.
    Bạn sẽ cần tìm các bài đăng có liên quan nhất trên HackerNews.
    """),
)

academic_paper_researcher = Agent(
    name="Nghiên cứu viên Giấy tờ Học thuật",
    model=OpenAIChat("gpt-4o-mini"),
    role="Nghiên cứu các giấy tờ học thuật và nội dung học thuật",
    tools=[GoogleSearchTools(), ArxivTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    Bạn là một nghiên cứu viên giấy tờ học thuật.
    Bạn sẽ được cho một chủ đề để nghiên cứu trong tài liệu học thuật.
    Bạn sẽ cần tìm các bài viết học thuật, giấy tờ, và các cuộc thảo luận học thuật có liên quan.
    Tập trung vào nội dung được đánh giá ngang hàng và các trích dẫn từ các nguồn tin cậy.
    Cung cấp tóm tắt ngắn gọn về các phát hiện chính và phương pháp luận.
    """),
)

twitter_researcher = Agent(
    name="Nghiên cứu viên Twitter",
    model=OpenAIChat("gpt-4o-mini"),
    role="Nghiên cứu các cuộc thảo luận đang thịnh hành và các cập nhật thời gian thực",
    tools=[DuckDuckGoTools()],
    add_name_to_instructions=True,
    instructions=dedent("""
    Bạn là một nghiên cứu viên Twitter/X.
    Bạn sẽ được cho một chủ đề để nghiên cứu trên Twitter/X.
    Bạn sẽ cần tìm các cuộc thảo luận đang thịnh hành, các tiếng nói có ảnh hưởng, và các cập nhật thời gian thực.
    Tập trung vào các tài khoản đã được xác minh và các nguồn tin cậy khi có thể.
    Theo dõi các hashtag có liên quan và các cuộc thảo luận đang diễn ra.
    """),
)


agent_team = Team(
    name="Đội ngũ Thảo luận",
    mode="collaborate",
    model=OpenAIChat("gpt-4o-mini"),
    members=[
        reddit_researcher,
        hackernews_researcher,
        academic_paper_researcher,
        twitter_researcher,
    ],
    instructions=[
        "Bạn là một người điều phối thảo luận.",
        "Bạn có nhiệm vụ dừng cuộc thảo luận khi bạn nghĩ rằng đội ngũ đã đạt được sự đồng thuận.",
    ],
    success_criteria="Đội ngũ đã đạt được sự đồng thuận.",
    enable_agentic_context=True,
    show_tool_calls=True,
    markdown=True,
    show_members_responses=True,
)
