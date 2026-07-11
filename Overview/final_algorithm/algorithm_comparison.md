# Báo cáo Phân tích Kiến trúc BOMA (Bayesian-Optimized Memetic Algorithm)

Bản báo cáo này phân tích chi tiết sự khác biệt giữa việc sử dụng các thuật toán đơn lẻ so với việc tích hợp chúng thành kiến trúc **Two-Phase BOMA** hiện tại. Đồng thời đánh giá khách quan về ưu nhược điểm và vạch ra các hướng đi trong tương lai.

---

## 1. Phân tích các thuật toán khi đứng độc lập

### A. Thuật toán Di truyền (HGA - Hybrid Genetic Algorithm)
- **Cơ chế:** Hoạt động dựa trên nguyên lý tiến hóa (Lai ghép, Đột biến, Chọn lọc tự nhiên) để thực hiện Tìm kiếm toàn cục (Global Search).
- **Điểm mạnh:** Có khả năng khám phá không gian giải pháp vô cùng rộng lớn. Rất khó bị kẹt ở "Cực tiểu cục bộ" (Local Optima) nhờ cơ chế đột biến đa dạng.
- **Điểm yếu:** "Làm thô rất tốt nhưng làm tinh rất tệ". HGA có thể dễ dàng nhét được 280/300 khách hàng, nhưng để tự nó nhét 20 khách cuối cùng là vô cùng chật vật và tốn thời gian (vì xác suất lai ghép trúng vị trí hoàn hảo ở phút chót là cực thấp).

### B. Tìm kiếm cục bộ (Local Search / Repair Operator)
- **Cơ chế:** Rút từng đơn hàng ra và thử chèn lại vào toàn bộ các khoảng trống thời gian hiện có để tìm vị trí tối ưu hơn.
- **Điểm mạnh:** Độ chính xác ở mức "phẫu thuật". Nó có thể nhồi nhét thành công những đơn hàng khó tính nhất (Time windows hẹp) vào những kẽ hở cực nhỏ của lịch trình.
- **Điểm yếu:** Chi phí tính toán là "Ác mộng" ($O(N^3)$). Nếu khởi điểm có quá nhiều đơn rớt, Local Search sẽ bị "ngộp" và treo máy vì phải duyệt qua hàng triệu phép thử ejections (rút-chèn).

### C. Tối ưu hóa Bayes (Bayesian Optimization - Optuna)
- **Cơ chế:** Dùng mô hình xác suất (TPE) để dự đoán giá trị tiếp theo.
- **Điểm yếu khi đứng độc lập:** Nó chỉ là một thuật toán "chỉ đường" (tìm bộ số), không thể tự mình xếp lịch trình cho xe tải.

---

## 2. Sự "Bổ khuyết" hoàn hảo của Kiến trúc Two-Phase

Kiến trúc mới không đơn thuần là "nhét chung" các thuật toán vào nhau, mà là một sự phân công lao động đỉnh cao theo 2 giai đoạn (Two-Phase):

> [!TIP]
> **Giai đoạn 1: Bayes + HGA (Training Phase)**
> Thay vì để HGA tự mò mẫm các hàm Heuristic (Solomon) bằng các trọng số cố định của con người (rất dễ sai lầm), **Bayes (Optuna)** đóng vai trò như một "Huấn luyện viên". Nó tinh chỉnh liên tục các trọng số (`Distance`, `Risk`, `Urgency`, `Waiting`) để tạo ra một "môi trường dễ thở nhất" cho HGA. 
> Nhờ có Bayes chỉ đường, HGA có thể dễ dàng chạm đến mốc chỉ rớt 2-3 đơn mà **không cần viện đến Local Search**.

> [!IMPORTANT]
> **Giai đoạn 2: HGA + Local Search (Generation Phase)**
> Nếu đặt Local Search vào vòng lặp của HGA (như kiến trúc cũ), hệ thống sẽ sụp đổ vì thời gian chạy quá lâu. 
> Ở kiến trúc mới, Local Search chỉ đóng vai trò **"Người gác đền cuối cùng" (Post-processing)**. HGA đã dọn sẵn một mâm cỗ hoàn hảo (297/300 đơn), Local Search chỉ việc nhảy vào đúng 1 lần duy nhất ở giây phút cuối cùng để dùng "dao mổ" xử lý nốt 3 đơn rớt. Nhờ vậy, tốc độ thuật toán từ **nhiều giờ đồng hồ** được nén xuống chỉ còn **vài phút**.

---

## 3. Đánh giá thuật toán mới nhất

### Ưu điểm vượt trội
1. **Tốc độ phi mã:** Việc tách rời Local Search ra khỏi quá trình Training giúp Optuna chạy hàng chục Trial chỉ trong vài chục phút.
2. **Khả năng đạt 100% (300/300):** Sự tinh tế của Local Search ở phút cuối đảm bảo lịch trình không bỏ sót bất kỳ khách hàng nào.
3. **Tiết kiệm quãng đường tối đa:** Thuật toán Penalty-based Tie-breaker của Optuna luôn thiên vị các kết quả có số Kilomet nhỏ nhất, ép chi phí xăng xe xuống mức cực thấp (từ 1758 km xuống 1597 km).

### Nhược điểm hiện đọng
1. **Phụ thuộc vào Dataset:** Bộ trọng số Vàng (Kim Cương) được Optuna tìm ra đang bị "Fit" (khớp) rất chặt với bộ dữ liệu Data_B hiện tại. Nếu chuyển sang một thành phố khác với địa hình khác, ta bắt buộc phải tốn 20 phút chạy lại quá trình Train.
2. **Tính ngẫu nhiên của HGA:** Mặc dù cùng một bộ Trọng số, nhưng vì HGA dựa trên ngẫu nhiên (Sinh sản, Đột biến), nên các lần chạy khác nhau có thể chênh lệch 1-2 đơn rớt.

---

## 4. Định hướng cải thiện trong tương lai

Để biến hệ thống này thành một sản phẩm Enterprise-grade (Cấp độ doanh nghiệp), đây là những hướng đi tiếp theo:

1. **Trọng số động (Dynamic Weights):** 
   Thay vì dùng 1 bộ trọng số cố định từ đầu đến cuối, ta có thể cho phép trọng số "Biến hình" theo từng thế hệ. Ví dụ: Những thế hệ đầu ưu tiên `Distance` để dồn xe, nhưng những thế hệ cuối tự động ưu tiên `Time Window` để vét khách.

2. **Song song hóa (Multi-threading / Multi-processing):**
   Hiện tại HGA đang đánh giá từng cá thể một cách tuần tự (Synchronous). Nếu chia 50 cá thể cho 8 nhân CPU chạy song song, thời gian sinh lịch trình sẽ giảm xuống dưới 10 giây.

3. **Predictive Insertion (Học Máy / Deep Learning):**
   Dùng một mạng Neural Network nhỏ học lại các quyết định của Local Search. Lần sau, thay vì thử nhét 90.000 vị trí, AI sẽ "nhìn" vào bản đồ và chỉ thẳng vị trí tốt nhất, xóa sổ hoàn toàn sự chậm chạp của hàm Heuristic.
