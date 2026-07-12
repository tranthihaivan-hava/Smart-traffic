# Tổng hợp Công thức Toán học: Solomon, Bayesian và Local Search

Tài liệu này cung cấp các công thức toán học lõi của 3 thành phần quan trọng nhất trong kiến trúc Two-Phase BOMA. Bạn có thể chép trực tiếp các công thức này vào báo cáo LaTeX.

---

## 1. Cấu trúc Không gian - Thời gian (Spatio-Temporal Mapping)

Điểm khác biệt cốt lõi trong codebase của bạn là sự liên kết giữa ma trận không gian (Distance) và trục thời gian thực (Time Windows) thông qua vận tốc vật lý. 

Giả sử khoảng cách Euclid giữa điểm $i$ và $j$ là $d_{ij}$ (đơn vị: km). Khi xe tải di chuyển với vận tốc trung bình không đổi $v = 50 \text{ km/h}$ (cấu hình `vehicle_speed`), thời gian di chuyển (Travel Time - tính bằng phút) được nội suy như sau:
$$ tt_{ij} = \frac{d_{ij}}{v} \times 60 $$

Từ đó, phương trình truy hồi cho thời gian xe đến (Arrival Time) tại điểm $j$ tiếp theo (sau khi phục vụ xong điểm $i$) là:
$$ Arrival_j = ServiceStart_i + ServiceDuration_i + tt_{ij} $$
*(Công thức này đóng vai trò quyết định để kiểm tra ràng buộc $Arrival_j \le WinEnd_j$ và tính toán đặc trưng $f_{wait}$)*.

---

## 2. Thuật toán chèn Solomon (Solomon I1 Insertion Heuristic)

Thuật toán Solomon I1 được sử dụng để xây dựng lộ trình khởi tạo bằng cách chèn từng khách hàng chưa được phục vụ vào vị trí tối ưu nhất trên lộ trình đang có.

Giả sử ta đang có một lộ trình một phần: $R = (i_0, i_1, \dots, i_m)$, trong đó $i_0$ và $i_m$ là Depot. Ta cần chèn khách hàng $u$ vào giữa hai điểm $i$ và $j$ liền kề trên $R$.

**Bước 1: Tính toán chi phí không gian (Khoảng cách tăng thêm)**
$$ c_1(i, u, j) = d_{iu} + d_{uj} - d_{ij} $$
*(Trong đó $d_{xy}$ là khoảng cách từ $x$ đến $y$)*

**Bước 2: Tính toán hàm mục tiêu tổng hợp (Fitness Score)**
Trong BOMA, chi phí chèn không chỉ phụ thuộc vào khoảng cách mà là tổ hợp tuyến tính của 4 đặc trưng đã được chuẩn hóa (Min-Max Scaler):
$$ c_2(i, u, j) = w_{dist}f_{dist}' + w_{urg}f_{urg}' + w_{wait}f_{wait}' + w_{risk}(1 - f_{risk}') $$

**Bước 3: Tiêu chuẩn chọn lựa chèn (Best Insertion)**
Vị trí chèn tốt nhất cho khách hàng $u$ là vị trí $(i, j)$ làm cực tiểu hóa hàm $c_2$:
$$ \text{Cost}(u) = \min_{i, j \in R} c_2(i, u, j) $$
Sau đó, thuật toán sẽ chọn khách hàng $u^*$ có $\text{Cost}(u^*)$ nhỏ nhất trong tất cả các khách hàng đang chờ để chính thức chèn vào lộ trình.

---

## 2. Tối ưu hóa Siêu tham số Bayes (Bayesian Optimization - TPE)

Hệ thống sử dụng bộ lấy mẫu TPE (Tree-structured Parzen Estimator) của thư viện Optuna để tìm vector trọng số $\mathbf{w} = [w_{dist}, w_{urg}, w_{wait}, w_{risk}]$.

Mục tiêu là tìm $\mathbf{w}$ làm cực tiểu hóa hàm chi phí toàn cục $y = f(\mathbf{w})$ (ví dụ: Tổng số đơn rớt và tổng quãng đường). TPE không mô hình hóa trực tiếp $P(y|\mathbf{w})$, mà mô hình hóa $P(\mathbf{w}|y)$ bằng cách chia lịch sử quan sát thành 2 nhóm dựa trên một ngưỡng $y^*$ (thường là top 15% kết quả tốt nhất):

$$ P(\mathbf{w}|y) = \begin{cases} \ell(\mathbf{w}) & \text{nếu } y < y^* \\ g(\mathbf{w}) & \text{nếu } y \ge y^* \end{cases} $$

*Trong đó:*
- $\ell(\mathbf{w})$ là mật độ phân phối của các trọng số mang lại kết quả **Tốt**.
- $g(\mathbf{w})$ là mật độ phân phối của các trọng số mang lại kết quả **Kém**.

**Hàm thu thập (Expected Improvement - EI):**
Để quyết định vector trọng số tiếp theo cần thử nghiệm, hệ thống tìm kiếm $\mathbf{w}$ làm cực đại hóa hàm Kỳ vọng cải thiện (EI). Theo TPE, $EI$ tỷ lệ thuận với tỷ số giữa hai phân phối trên:

$$ EI(\mathbf{w}) \propto \frac{\ell(\mathbf{w})}{g(\mathbf{w})} $$

$$ \mathbf{w}_{next} = \arg\max_{\mathbf{w}} \frac{\ell(\mathbf{w})}{g(\mathbf{w})} $$
Thuật toán sẽ tự động sinh ra trọng số mới có xác suất rơi vào nhóm $\ell(\mathbf{w})$ cao nhất.

---

## 3. Khôi phục cục bộ (Local Search Repair Operator)

Local Search được áp dụng ở pha cuối (Phase 2) để cải thiện một giải pháp $S$ hiện tại bằng cách di chuyển nó sang một giải pháp lân cận $S' \in N(S)$ tốt hơn.

**Hàm Đánh giá độ chênh lệch (Delta Cost):**
$$ \Delta = \text{Cost}(S') - \text{Cost}(S) $$
Thuật toán chấp nhận $S'$ nếu $\Delta \le 0$ (Greedy Descent) VÀ $S'$ không vi phạm bất kỳ cửa sổ thời gian nào.

**Các toán tử lân cận (Neighborhood Operators):**
1. **Relocate (Dịch chuyển):** Rút khách hàng $u$ từ lộ trình $R_1$ và chèn vào vị trí $k$ trên lộ trình $R_2$.
   $$ \Delta_{relocate} = (d_{i,k} + d_{k,j} - d_{i,j}) - (d_{x,u} + d_{u,y} - d_{x,y}) $$
2. **Swap (Hoán đổi):** Tráo đổi vị trí của khách hàng $u \in R_1$ và $v \in R_2$.
   $$ \Delta_{swap} = (d_{i,v} + d_{v,j} + d_{x,u} + d_{u,y}) - (d_{i,u} + d_{u,j} + d_{x,v} + d_{v,y}) $$
3. **2-opt (Gỡ nút thắt):** Đảo ngược trình tự một đoạn khách hàng từ vị trí $i$ đến $j$ trên cùng một lộ trình để loại bỏ các đường chéo cắt nhau.
   $$ \Delta_{2opt} = d_{i-1, j} + d_{i, j+1} - d_{i-1, i} - d_{j, j+1} $$

*(Lưu ý: Mọi phép biến đổi $S'$ sinh ra từ 3 toán tử trên đều phải vượt qua hàm `validate_time_windows()` để đảm bảo $Arrival_i \le WinEnd_i \quad \forall i \in S'$).*
