# Luồng Hoạt Động (Flow) Của Toàn Bộ Hệ Thống

Dưới đây là luồng hoạt động (flow) của toàn bộ hệ thống từ đầu đến cuối, được tóm tắt ngắn gọn và mạch lạc:

**1. Data (Dữ liệu gốc)**
`locations.csv` (tọa độ, thời gian dỡ hàng) + `time_windows.csv` (khung giờ mở cửa).

⬇️

**2. Preprocessing (Tiền xử lý)**
Nạp data thông qua `DatasetLoader` ➡️ Parse thành các object `Customer` ➡️ Tính toán toàn bộ `DistanceMatrix` (khoảng cách Euclidean) và `TravelTimeMatrix` (thời gian đi lại dựa trên v=50km/h).

⬇️

**3. Modeling (Mô hình hoá)**
Gom tất cả các Matrix và Customer vào một object trung tâm là `Problem` (Đại diện cho toàn bộ bài toán).

⬇️

**4. Weights (Trọng số Tối ưu)**
Khởi tạo `WeightVector` gồm 4 hệ số: *khoảng cách, độ gấp gáp, thời gian chờ, rủi ro giao hàng*. (Bộ số này trước đó đã được train bằng thuật toán AI `Bayesian Optimization` để mò ra điểm cân bằng hoàn hảo nhất).

⬇️

**5. Solver (Giải thuật cốt lõi)**
Nạp `Problem` và `WeightVector` vào `GreedySolver`.

⬇️

**6. Routing (Xây dựng Lộ trình - Solomon Insertion)**
`GreedySolver` chạy vòng lặp 7 ngày. Ở mỗi ngày, nó dùng thuật toán *Solomon Insertion* kết hợp với *Objective Function* (Hàm mục tiêu):
- Thử chèn từng khách hàng chưa giao vào lộ trình.
- Chấm điểm (Score) từng khách hàng dựa trên 4 trọng số ở bước (4).
- Ai điểm cao nhất (gần nhất, sắp trễ giờ, ít phải chờ nhất) và HỢP LỆ (không vi phạm time window) thì nhét vào tuyến đường. Lặp lại cho đến khi hết ngày.

⬇️

**7. Repair (Sửa chữa / Tối đa hoá)**
Gọi `RepairOperator` quét lại xem còn khách hàng nào bị rớt lại không. Nếu có, nó cố gắng bẻ cong một chút ràng buộc mềm để chèn nốt vào, đảm bảo mục tiêu tối đa 300/300 khách.

⬇️

**8. State (Bộ nhớ Kết quả)**
Lưu toàn bộ lộ trình hoàn chỉnh vào bộ nhớ `State` (bao gồm 7 mảng lộ trình cho 7 ngày).

⬇️

**9. Display & Visualize (Hiển thị)**
Truyền mảng kết quả đó vào các script `generate_detailed_schedule.py` và `generate_visuals.py` ➡️ Tự động tính lùi (shift) giờ xuất phát để loại bỏ giờ chờ chết ở kho ➡️ Xuất ra bảng lịch trình Markdown và 5 biểu đồ PNG như bạn thấy.
