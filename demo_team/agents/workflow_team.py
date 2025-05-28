
from collections.abc import Iterator
from textwrap import dedent

from agno.agent import Agent, RunResponse
from agno.models.openai import OpenAIChat
from agno.team.team import Team
from agno.tools.hackernews import HackerNewsTools
from agno.tools.newspaper4k import Newspaper4kTools
from agno.utils.log import logger
from agno.workflow import Workflow


class TeamWorkflow(Workflow):
    description: str = (
        "Lấy các câu chuyện hàng đầu từ Hacker News và Reddit và viết một báo cáo về chúng."
    )

    reddit_researcher = Agent(
        name="Nhà nghiên cứu Reddit",
        role="Nghiên cứu một chủ đề trên Reddit",
        model=OpenAIChat(id="gpt-4o"),
        add_name_to_instructions=True,
        instructions=dedent("""
            Bạn là một nhà nghiên cứu Reddit.
            Bạn sẽ được giao một chủ đề để nghiên cứu trên Reddit.
            Bạn cần tìm các bài đăng liên quan nhất trên Reddit.
        """),
    )

    hackernews_researcher = Agent(
        name="Nhà nghiên cứu HackerNews",
        model=OpenAIChat("gpt-4o"),
        role="Nghiên cứu một chủ đề trên HackerNews.",
        tools=[HackerNewsTools()],
        add_name_to_instructions=True,
        instructions=dedent("""
            Bạn là một nhà nghiên cứu HackerNews.
            Bạn sẽ được giao một chủ đề để nghiên cứu trên HackerNews.
            Bạn cần tìm các bài đăng liên quan nhất trên HackerNews.
        """),
    )

    agent_team = Team(
        name="Đội Thảo luận",
        mode="collaborate",
        model=OpenAIChat("gpt-4o"),
        members=[
            reddit_researcher,
            hackernews_researcher,
        ],
        instructions=[
            "Bạn là một điều phối viên thảo luận.",
            "Vai trò chính của bạn là tạo điều kiện cho quá trình nghiên cứu.",
            "Khi cả hai thành viên trong nhóm đã cung cấp kết quả nghiên cứu của họ với các liên kết đến các câu chuyện hàng đầu từ các nền tảng tương ứng (Reddit và HackerNews), bạn nên dừng cuộc thảo luận.",
            "Không tiếp tục cuộc thảo luận sau khi nhận được các liên kết - mục tiêu của bạn là thu thập kết quả nghiên cứu, không phải để đạt được sự đồng thuận về nội dung.",
            "Đảm bảo mỗi thành viên cung cấp các liên kết liên quan với mô tả ngắn gọn trước khi kết thúc.",
        ],
        success_criteria="Nhóm đã đạt được sự đồng thuận.",
        enable_agentic_context=True,
        show_tool_calls=True,
        markdown=True,
        debug_mode=True,
        show_members_responses=True,
    )

    writer: Agent = Agent(
        tools=[Newspaper4kTools()],
        description="Viết một báo cáo hấp dẫn về các câu chuyện hàng đầu từ nhiều nguồn khác nhau.",
        instructions=[
            "Bạn sẽ nhận được các liên kết đến các câu chuyện hàng đầu từ Reddit và HackerNews từ nhóm agent.",
            "Nhiệm vụ của bạn là truy cập các liên kết này và đọc kỹ từng bài báo.",
            "Trích xuất thông tin chính, những hiểu biết sâu sắc và các điểm đáng chú ý từ mỗi nguồn.",
            "Viết một báo cáo toàn diện, có cấu trúc tốt tổng hợp thông tin.",
            "Tạo một tiêu đề hấp dẫn và thu hút cho báo cáo của bạn.",
            "Tổ chức nội dung thành các phần liên quan với các tiêu đề mô tả.",
            "Đối với mỗi bài báo, bao gồm nguồn, tiêu đề, URL và tóm tắt ngắn gọn.",
            "Cung cấp phân tích chi tiết và bối cảnh cho những câu chuyện quan trọng nhất.",
            "Kết thúc với các điểm chính tóm tắt những hiểu biết chính.",
            "Duy trì giọng điệu chuyên nghiệp tương tự như báo cáo của New York Times.",
            "Nếu bạn không thể truy cập hoặc hiểu một số bài báo, hãy ghi chú điều này và tập trung vào những bài bạn có thể phân tích.",
        ],
    )

    def run(self, message: str) -> Iterator[RunResponse]:
        logger.info("Đang lấy các câu chuyện hàng đầu từ HackerNews.")
        discussion: RunResponse = self.agent_team.run(message)
        if discussion is None or not discussion.content:
            yield RunResponse(
                run_id=self.run_id, content="Xin lỗi, không thể lấy được các câu chuyện hàng đầu."
            )
            return

        logger.info("Đang đọc từng câu chuyện và viết báo cáo.")
        yield from self.writer.run(discussion.content, stream=True)
