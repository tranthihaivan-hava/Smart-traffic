# Giải mã 4 Trọng số (Weights) trong Kiến trúc BOMA

Hệ thống BOMA sử dụng 4 trọng số do Bayesian Optimization (Optuna) tìm ra để đánh giá mức độ "phù hợp" khi quyết định có chèn một khách hàng vào lộ trình hay không. Việc tính toán điểm số (Score) của mỗi ứng viên luôn tuân theo nguyên tắc: **Điểm Score càng THẤP thì khách hàng càng ĐƯỢC ƯU TIÊN giao ngay.**

Dưới đây là định nghĩa và công thức toán học nội tại (Raw Features) được trích xuất trực tiếp từ bộ dữ liệu gốc (Dataset) cho 4 thành phần này.

---

### 1. Đặc trưng Khoảng cách ($f_{dist}$) và Trọng số ($w_{dist}$)
**Ý nghĩa:** Đại diện cho mức độ làm "phình to" lộ trình hiện tại nếu quyết định chèn khách hàng vào. Hệ thống muốn tìm khách hàng ở gần nhất dọc theo cung đường đang chạy.

**Công thức gốc (Feature $f_{dist}$):** Khi chèn khách hàng $C$ vào giữa 2 điểm $A$ và $B$ trên lộ trình:
$$ f_{dist} = D(A, C) + D(C, B) - D(A, B) $$
*Trong đó:*
- $D(x, y)$ là ma trận khoảng cách từ điểm $x$ đến điểm $y$.

---

### 2. Đặc trưng Khẩn cấp ($f_{urg}$) và Trọng số ($w_{urg}$)
**Ý nghĩa:** Đại diện cho áp lực thời gian (Deadline). Khách hàng nào sắp bị đóng cửa sổ giao hàng (Time Window) sẽ có độ khẩn cấp cao. Hệ thống phải ưu tiên giao cho người sắp "hết hạn" trước.

**Công thức gốc (Feature $f_{urg}$):**
$$ f_{urg} = WinEnd - T_{current} $$
*Trong đó:*
- $WinEnd$ là thời gian Đóng cửa sổ (theo phút tính từ 00:00) của khách hàng đó trong ngày hiện tại.
- $T_{current}$ là thời gian hiện tại của chiếc xe tải đang chạy.
*(Ví dụ: Cửa hàng đóng cửa lúc 16:00 (960 phút). Bây giờ là 15:30 (930 phút). $f_{urg} = 960 - 930 = 30$ phút. Giá trị này rất thấp -> Cực kỳ khẩn cấp).*

---

### 3. Đặc trưng Thời gian chờ ($f_{wait}$) và Trọng số ($w_{wait}$)
**Ý nghĩa:** Nếu xe tải chạy đến nhà khách hàng quá sớm (khi họ chưa mở cửa), tài xế bắt buộc phải đỗ xe ngồi chờ. Hệ thống cố gắng tránh điều này để tối ưu hóa năng suất ca làm việc.

**Công thức gốc (Feature $f_{wait}$):**
$$ f_{wait} = \max(0, WinStart - ArrivalTime) $$
*Trong đó:*
- $WinStart$ là thời điểm Mở cửa sổ giao hàng của khách.
- $ArrivalTime$ là thời gian xe tải đến nơi.
*(Ví dụ: Tới nơi lúc 8h sáng, nhưng 9h sáng khách mới mở cửa. Thời gian chờ $f_{wait} = 60$ phút).*

---

### 4. Đặc trưng Rủi ro Giao hàng ($f_{risk}$) và Trọng số ($w_{risk}$)
**Ý nghĩa:** Một số khách hàng cực kỳ "khó tính", cả tuần họ chỉ mở cửa đúng 1 lần vào Thứ 2. Một số khách hàng khác thì "dễ tính", ngày nào cũng nhận hàng. Hệ thống tính toán Rủi ro này để ưu tiên "giải quyết" những khách hàng khó tính trước, tránh việc để dành đến cuối tuần rồi không còn ngày nào giao được.

**Công thức gốc (Feature $f_{risk}$):**
$$ f_{risk} = \frac{1}{|W_{remaining}| \times (Days_{max} - d_{current} + 1)} $$
*Trong đó:*
- $|W_{remaining}|$ là tổng số cửa sổ thời gian (Time Windows) CÒN LẠI của khách hàng tính từ hôm nay đến hết tuần.
- $Days_{max}$ là tổng số ngày của đợt giao (Ví dụ 7 ngày).
- $d_{current}$ là ngày hiện tại đang chạy thuật toán.

*(Lưu ý: Vì khách hàng càng "hiếm" cửa sổ thì $f_{risk}$ càng CAO, nhưng thuật toán lại ưu tiên điểm số THẤP, do đó trong bước Chuẩn hóa (Normalization) ở file `normalizer.py`, giá trị này đã được đảo ngược lại bằng công thức `1.0 - scaled_risk` để đồng bộ cơ chế tối ưu).*

---

### TỔNG HỢP (Hàm Thích nghi - Fitness Score)

Sau khi tính toán được 4 đặc trưng thô (Raw Features) kể trên, chúng sẽ được Min-Max Scaler chuẩn hóa về biên độ `[0, 1]`. Điểm số cuối cùng của mỗi lựa chọn sẽ là tích chập tuyến tính với 4 trọng số của Optuna:

$$ Score = (w_{dist} \cdot f_{dist}') + (w_{urg} \cdot f_{urg}') + (w_{wait} \cdot f_{wait}') + (w_{risk} \cdot (1 - f_{risk}')) $$

Lựa chọn nào có **$Score$ nhỏ nhất** sẽ được hệ thống chốt để đi tiếp (Greedy Selection) trong mỗi bước nội suy của thuật toán.
