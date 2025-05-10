from agno.tools import tool


@tool(name="send_card_ticket", description="Sử dụng hàm này để gửi support_code để bộ phận kỹ thuật vào hổ trợ.")
def send_card_ticket(support_code: str) -> str:
    """Sử dụng hàm này để gửi support_code để bộ phận kỹ thuật vào hổ trợ.
    Args:
        support_code (str): support_code
    Returns:
        str: thông báo lại người dùng
    """
    print(f"Đã gửi thành công code {support_code}")
    return f"Đã gửi thành công code {support_code}"
