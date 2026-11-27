# Lab 6 — H2 reflection (nhat_dm)

Explain RAG to a friend who never studied AI, using the picture of an open-book exam. Mention at least one
thing **our code** checks that the model does not (e.g. the grounding check, or the `min_score` threshold).
Exactly 5 lines between the markers, in your own words (English or Vietnamese). Do not copy a teammate.

<!-- reflection:start -->
RAG giống như một thí sinh bước vào phòng thi mở sách (open-book exam) với cuốn cẩm nang quy chế được phép mang theo.
Thay vì bắt học sinh nhớ vẹt mọi điều luật dễ dẫn đến việc bịa đặt đáp án (hallucination), hệ thống tìm đúng trang cẩm nang phù hợp nhất với câu hỏi.
Học sinh sau đó đọc kỹ trang sách đó để tổng hợp câu trả lời chính xác và kèm theo dẫn chứng cụ thể.
Điều khác biệt là code của chúng ta cài đặt cơ chế kiểm tra đối chiếu (grounding check) và ngưỡng điểm tin cậy min_score khắt khe.
Nếu độ tương đồng dưới ngưỡng hoặc mô hình trích dẫn nguồn không có trong tài liệu tra cứu, hệ thống lập tức từ chối trả lời (abstain) để đảm bảo an toàn.
<!-- reflection:end -->
