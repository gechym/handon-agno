## Ý tưởng

- Ý tưởng được bắt đầu từ blog của Anthopic `https://www.anthropic.com/engineering/claude-think-tool`. Blog này để cập đến việc nâng cao khả năng xử lý vấn đề người dùng của các mô hình `Claude`.
- **Vấn đề:** Các mô hình ngôn ngữ lớn (LLM) rất mạnh mẽ, nhưng chúng vẫn gặp khó khăn trong các tác vụ yêu cầu lập luận nhiều bước, ghi nhớ thông tin trước đó hoặc cần suy nghĩ sâu sắc để thực hiện đúng vấn đề.
- **Giải quyết:**

  - Anthopic cung cấp một công cụ `think` nó như các công cụ bình thường mà người dùng thường truyền vào. Nhưng công cụ này có mục đích là nơi `làm nháp` cho mô hình.
  - Ví dụ chúng ta có một bài toán khó cần xử lý nhiều bước mới đưa ra được kết quả. Nhưng những mô hình không hỗ trợ thinking sẽ có xu hướng đưa ra luôn kết quả. Đến lúc này tool `think` sẽ là nơi `làm nháp` cho các mô hình này. Các mô hình sẽ gọi tool này để đưa ra những suy nghĩ của nó về vấn đề của người dùng. Và khi vấn đề chưa được rõ nó lại tiếp tục thực hiện gọi tool `think` cho đến khi có được kết quả cuối cùng.

- **Cách thức hoạt động:**

  - Sau khi mô hình thực hiện một hành động `(call tool)` hay chuẩn bị đưa ra đáp án cuối cùng cho người dùng. Thì mô hình sẽ gọi hàm tool `think` (nếu chúng có suy nghĩ là cần sử dụng nháp). Tool `think` sẽ được gọi và mô hình sẽ đưa ra suy nghĩ, đánh giá của mình trước khi có các hành động tiếp theo.

- **Đánh giá**
  - Anthopic có đưa ra đánh giá dựa trên 1 benchmark là `tau-bench`...

## Các Tool được Agno xây dựng

### 1.
