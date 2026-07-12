# Hướng Dẫn Viết Báo Cáo: Phần Kết Quả & Mô Phỏng

Tài liệu này được biên soạn để giúp bạn xây dựng **Chương 4: Kết quả Thực nghiệm & Mô phỏng** và **Chương 5: Đánh giá Ưu nhược điểm** một cách học thuật, thuyết phục và làm nổi bật được sự tinh tế của kiến trúc Two-Phase BOMA.

---

## 1. Cấu trúc Chương Kết Quả & Mô Phỏng

Thay vì chỉ ném kết quả vào báo cáo, bạn nên trình bày theo mạch logic: **Từ tổng quan đến chi tiết, từ so sánh đến hiệu năng thực tế.**

### 1.1. So sánh Thuật toán (Benchmark Comparison)
* **Mục đích:** Chứng minh lý do tại sao hệ thống lại cần đến HGA thay vì chỉ dùng Thuật toán Tham lam (Greedy).
* **Hình ảnh sử dụng:** `fig_method_comparison.png`
* **Nội dung cần viết:**
  - Trình bày biểu đồ so sánh giữa Greedy Solver và HGA Solver.
  - Nhấn mạnh vào 2 thông số:
    1. **Tỷ lệ phục vụ (Served Customers):** HGA (kết hợp Local Search) đạt mức tuyệt đối 300/300, trong khi thuật toán Greedy cơ bản bị rớt lại rất nhiều đơn.
    2. **Tổng quãng đường (Total Distance):** Dù phục vụ nhiều khách hơn, HGA vẫn tối ưu hóa được quãng đường di chuyển nhờ cơ chế Crossover/Mutation và hàm Heuristic được lai tạo.
  - **Kết luận tiểu mục:** BOMA-HGA vượt trội hoàn toàn về cả Capacity (sức chứa) lẫn Cost (chi phí).

### 1.2. Phân bổ Tải trọng theo Ngày (Daily Workload Distribution)
* **Mục đích:** Chứng minh tính thực tế của lịch trình, không bị dồn việc vào một ngày duy nhất gây quá tải cho tài xế.
* **Hình ảnh sử dụng:** `fig_daily_customers.png` và `fig_customer_distribution.png`
* **Nội dung cần viết:**
  - Báo cáo biểu đồ cột (Bar chart) cho thấy số lượng khách hàng được phục vụ tăng dần từ Thứ 2 đến Chủ nhật (đỉnh điểm vào T7, CN).
  - Điều này chứng minh thuật toán có khả năng gom nhóm (Clustering) các khách hàng có Time Windows rải rác về các ngày cuối tuần để tối ưu lộ trình.
  - Đưa Pie chart (100% Served) vào để khẳng định tính toàn vẹn của mô hình.

### 1.3. Mô phỏng Ca làm việc Thực tế (Shift Timeline Simulation)
* **Mục đích:** Đưa toán học vào thực tiễn, cho thấy lịch làm việc của tài xế (Shipper) là hoàn toàn hợp lý và khả thi.
* **Hình ảnh sử dụng:** `fig_shift_timeline.png`
* **Nội dung cần viết:**
  - Giải thích trục thời gian (Gantt chart).
  - Chỉ ra rằng: Thuật toán đã tự động tính toán **Giờ xuất phát tối ưu** cho từng ngày (ví dụ không xuất phát lúc 0h sáng, mà lùi giờ xuất phát đến 7h-9h sáng để khớp với thời gian mở cửa của khách hàng đầu tiên).
  - Đây là minh chứng cho trí thông minh của hệ thống: Tối ưu hóa thời gian chờ (Waiting time) ngay tại Depot trước khi lăn bánh.

### 1.4. Trực quan hóa Mạng lưới Di chuyển (Spatial Route Network)
* **Mục đích:** Cho người xem (Hội đồng) thấy độ phức tạp không gian (Spatial Complexity) của bài toán 300 đỉnh (nodes).
* **Hình ảnh sử dụng:** `fig_route_map_network.png`
* **Nội dung cần viết:**
  - Bản đồ thể hiện các quỹ đạo di chuyển chằng chịt nhưng được gom cụm rất tốt quanh Depot (Ngôi sao ở giữa).
  - Dù không có tọa độ địa lý thực, thuật toán vẫn vẽ ra được một mạng lưới di chuyển dạng "cánh hoa" (Petal-shaped routes) - đây là hình thái tối ưu kinh điển của các bài toán VRP.

### 1.5. Trích xuất Lịch trình Chi tiết (Detailed Schedule)
* **Hình ảnh sử dụng:** Chụp 1-2 ngày trong file `detailed_schedule.md` làm ví dụ.
* **Nội dung cần viết:**
  - Giải thích cấu trúc một dòng dữ liệu (Arrival -> Wait -> Service Start -> Departure).
  - Giải thích cách hệ thống tính toán khắt khe từng phút để không vi phạm "All Windows".

---

## 2. Phần Đánh giá Ưu - Nhược điểm (Evaluation)

Đây là phần để bạn thể hiện **Tư duy phản biện (Critical Thinking)**. Đừng chỉ khen ngợi hệ thống, hãy chỉ ra cả những điểm giới hạn.

### 2.1. Ưu điểm Vượt trội (Pros)
1. **Kiến trúc Two-Phase tách bạch hoàn hảo:** Việc đưa Optuna (AI) ra ngoài làm "Huấn luyện viên" giúp HGA chạy cực kỳ nhẹ nhàng bên trong mà không bị tắc nghẽn tính toán.
2. **Cứu hộ độ chính xác cao (Repair Operator):** Thay vì bắt HGA tự dò dẫm 100% (rất tốn thời gian), hệ thống để HGA làm 98% công việc, và dùng Local Search (Repair) nhảy vào đúng 1 lần duy nhất ở giây phút cuối cùng để gắp nốt 2% đơn hàng bị rớt nhét vào khe hở. Đây là chiến thuật "Dao mổ trâu" và "Kim chỉ" kết hợp cực kỳ thông minh.
3. **Phát hiện thú vị về đánh đổi Tối ưu (Trade-off Insight):** 
   - Trọng số Optuna tìm ra có **`Waiting = 0.042`** (rất thấp) trong khi **`Distance = 0.887`** (rất cao).
   - Hệ thống chấp nhận việc tài xế đến sớm và phải chờ đợi vài tiếng đồng hồ tại điểm giao, miễn là không làm tăng tổng số Kilomet di chuyển. Điều này hoàn toàn hợp lệ với bài toán Toán học và giúp ép chi phí xăng xe xuống mức cực hạn.

### 2.2. Nhược điểm & Hạn chế (Cons)
1. **Overfitting với Dataset (Phụ thuộc dữ liệu):**
   - Bộ trọng số hiện tại (`Dist=0.887, Urg=0.496, Wait=0.042, Risk=0.888`) được tinh chỉnh "đo ni đóng giày" cho địa hình của Data_B. 
   - Nếu bê bộ số này sang một thành phố khác (Data_C), nó có thể không còn là tối ưu nhất. Người dùng bắt buộc phải tốn thời gian chạy lại Phase 1 (Optuna) mỗi khi có bản đồ mới.
2. **Không đa dạng hóa loại xe (Single Fleet Limit):**
   - Hiện tại thuật toán đang giả định tài xế làm việc xuyên suốt nhiều ngày với tải trọng vô hạn (hoặc tải trọng không bị siết chặt trong thực nghiệm). Thực tế cần tích hợp thêm giới hạn sức chứa (Capacity) và sử dụng nhiều xe khác nhau trong cùng một ngày.

---

## 3. Lời khuyên khi lên Thuyết trình (Defense Tips)

- **Chuẩn bị sẵn file `presentation_result.txt`:** Nếu hội đồng yêu cầu chạy lại hoặc hỏi tại sao kết quả vẽ biểu đồ và bảng tính lại giống hệt nhau không lệch một giây, hãy giải thích khái niệm **"Single Source of Truth"** (Đóng băng kết quả ngẫu nhiên để phục vụ Báo cáo).
- **Mở file `detailed_schedule.md`:** Hãy mở file này trên IDE và cuộn cho hội đồng xem. Khối lượng dữ liệu khổng lồ (vài trăm dòng lịch trình chi tiết từng phút) sẽ là minh chứng mạnh mẽ nhất cho khối lượng công việc hệ thống đã xử lý.
