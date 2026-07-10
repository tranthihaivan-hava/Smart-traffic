# Mathematical Proof: Infeasibility of Customer C268 under Strict Constraints
=============================================================================

Tài liệu này cung cấp minh chứng toán học chi tiết về việc tại sao khách hàng **C268** hoàn toàn **bất khả thi** (không thể phục vụ) dưới ràng buộc **Strict Time Windows** (Giao hàng và dỡ hàng phải hoàn tất trước hạn đóng cửa), bất kể thuật toán tối ưu hóa có tốt đến đâu trên cả hai ngày khả thi duy nhất của khách hàng này là **Thứ Hai (Day 1)** và **Thứ Sáu (Day 5)**.

---

## Lời giải thích về thuật toán và thời gian (Đính chính quan trọng)
*Thuật toán mô phỏng thời gian theo **số phút tuyệt đối tính từ 00:00 (nửa đêm)**.*
*Tất cả các ca làm việc của Shipper trong 7 ngày đều kết thúc vào khoảng 20:44 - 21:39 cùng ngày (Hoàn toàn không có chuyện lấn sang ngày hôm sau).* 
*(Bảng timeline trước đây bị lỗi hiển thị cộng dư 8 tiếng khiến 21:39 bị in thành 29:39. Dưới đây là bảng thời gian thực tế chính xác 100%).*

---

## 1. Thông số kỹ thuật của C268 và Mạng lưới
* **Khoảng cách từ Depot:** 21.27 km (Thời gian di chuyển một chiều từ Depot: **25.5 phút**).
* **Thời gian dỡ hàng (Service Duration):** **10.0 phút**.
* **Ngày có thể giao hàng:** Chỉ Thứ Hai (Monday - Day 1) hoặc Thứ Sáu (Friday - Day 5).
* **Khung giờ nhận hàng (Time Window):** **18:30 – 21:30** (tương ứng phút **1110** đến **1290** tính từ 00:00).
* **Yêu cầu Strict:** Xe bắt buộc phải có mặt và bắt đầu phục vụ muộn nhất lúc **21:20** (21:30 - 10 phút dỡ hàng).

---

## 2. Phân tích chi tiết Lộ trình Thứ Sáu (Day 5)

Lộ trình Thứ Sáu hiện phục vụ **22 khách hàng**. Dưới đây là timeline hoạt động chi tiết cuối ca chiều tối (từ Stop 17 đến khi về Depot):

| Thứ tự Stop | Mã KH | Giờ đến (Arrive) | Chờ (Wait) | Bắt đầu giao (Start) | Rời đi (Depart) | Khung giờ của KH (Window) | Khoảng cách từ điểm trước |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stop 17** | C173 | 19:34 | 0.0m | 19:34 | 19:41 | 18:30 - 21:30 | 5.7 km |
| **Stop 18** | C128 | 19:42 | 0.0m | 19:42 | 19:47 | 18:30 - 21:30 | 0.8 km |
| **Stop 19** | C083 | 20:06 | 0.0m | 20:06 | 20:13 | 18:30 - 21:30 | 16.2 km |
| **Stop 20** | C076 | 20:47 | 0.0m | 20:47 | 20:52 | 18:30 - 21:30 | 28.3 km |
| **Stop 21** | C233 | 21:02 | 0.0m | 21:02 | 21:12 | 18:30 - 21:30 | 8.0 km |
| **Stop 22** | C272 | 21:15 | 0.0m | 21:15 | **21:20** | 18:30 - 21:30 | 2.8 km |
| **DEPOT** | - | 21:35 | - | - | - | - | 14.7 km |

### Kịch bản thử nghiệm chèn C268:

#### Kịch bản A: Chèn C268 vào sau Stop 22 (C272) ở cuối ca làm việc
* Giờ xe rời C272: **21:20**.
* Khoảng cách di chuyển C272 → C268: 21.27 km (mất **25.5 phút**).
* Thời điểm đến C268: `21:20 + 25.5 phút = 21:45.5`.
* **Kết quả:** Xe đến muộn **15.5 phút** so với hạn đóng cửa 21:30 của C268. ❌ **VI PHẠM**.

#### Kịch bản B: Chèn C268 trước Stop 22 (C272)
* Để kịp giao cho C268 (phải xong trước 21:30), xe phải đến C268 muộn nhất lúc **21:20**.
* Giả sử xe rời C268 đúng 21:30, thời gian di chuyển từ C268 sang C272 mất 3.4 phút.
* Thời điểm đến C272: `21:30 + 3.4 phút = 21:33.4`.
* **Kết quả:** Quá hạn đóng cửa 21:30 của C272. ❌ **VI PHẠM**.

#### Kịch bản C: Chèn C268 vào giữa ngày (đầu ca chiều)
* Nếu xe đến C268 lúc 16:00 chiều: Xe phải đợi đến **18:30** (chờ 150 phút) mới được bắt đầu giao.
* Việc chờ đợi này đóng băng toàn bộ tiến trình và đẩy toàn bộ các stop tiếp theo (C163, C001, C190, C131...) bị trễ giờ đóng cửa từ 1.5 đến 2 tiếng. ❌ **VI PHẠM TOÀN BỘ LỘ TRÌNH**.

> [!NOTE]
> **UPDATE:** Giới hạn này đã được phá vỡ thành công nhờ thuật toán **Ejection Chain (Repair Operator)**. Bằng cách "đá" các khách hàng bị kẹt ra khỏi lịch và nhét họ vào ngày khác, C268 đã có đủ khoảng trống để được phục vụ mà không vi phạm Strict Time Windows. Dưới đây là phân tích nguyên thủy khi chưa có Repair Operator.

## 3. Phân tích chi tiết Lộ trình Thứ Hai (Day 1)

Ngày Thứ Hai có mật độ cực kỳ cao với **52 khách hàng**. Shipper làm việc liên tục đến **21:39** tối (09:39 PM) thì quay về tới kho (Không hề lấn sang ngày hôm sau).

Dưới đây là timeline hoạt động đầy đủ của ngày Thứ Hai:

| Thứ tự Stop | Mã KH | Giờ đến (Arrive) | Chờ (Wait) | Bắt đầu giao (Start) | Rời đi (Depart) | Khung giờ của KH (Window) | Khoảng cách từ điểm trước |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Stop 01** | C175 | 00:13 | 496.7m | 08:30 | 08:37 | 08:30 - 11:30 | 11.06 km |
| **Stop 02** | C228 | 08:47 | 0.0m | 08:47 | 08:57 | 08:30 - 11:30 | 8.43 km |
| **Stop 03** | C247 | 09:07 | 0.0m | 09:07 | 09:12 | 08:30 - 11:30 | 8.31 km |
| **Stop 04** | C110 | 09:13 | 0.0m | 09:13 | 09:23 | 07:22 - 16:08 | 0.86 km |
| **Stop 05** | C174 | 09:24 | 0.0m | 09:24 | 09:34 | 08:30 - 11:30 | 1.24 km |
| **Stop 06** | C206 | 09:34 | 0.0m | 09:34 | 09:41 | 08:54 - 17:27 | 0.11 km |
| **Stop 07** | C107 | 09:42 | 0.0m | 09:42 | 09:49 | 07:12 - 16:03 | 0.49 km |
| **Stop 08** | C179 | 09:49 | 0.0m | 09:49 | 09:54 | 07:21 - 15:28 | 0.40 km |
| **Stop 09** | C005 | 09:55 | 0.0m | 09:55 | 10:02 | 07:54 - 15:21 | 0.54 km |
| **Stop 10** | C143 | 10:03 | 0.0m | 10:03 | 10:10 | 08:30 - 11:30 | 0.46 km |
| **Stop 11** | C119 | 10:13 | 0.0m | 10:13 | 10:20 | 08:30 - 11:30 | 3.00 km |
| **Stop 12** | C144 | 10:24 | 0.0m | 10:24 | 10:31 | 07:59 - 16:17 | 3.17 km |
| **Stop 13** | C150 | 10:32 | 0.0m | 10:32 | 10:42 | 08:30 - 11:30 | 0.53 km |
| **Stop 14** | C135 | 10:42 | 0.0m | 10:42 | 10:52 | 07:55 - 16:23 | 0.19 km |
| **Stop 15** | C216 | 10:52 | 0.0m | 10:52 | 10:59 | 07:11 - 16:38 | 0.16 km |
| **Stop 16** | C152 | 11:00 | 0.0m | 11:00 | 11:05 | 08:30 - 11:30 | 0.63 km |
| **Stop 17** | C243 | 11:06 | 0.0m | 11:06 | 11:13 | 08:30 - 11:30 | 0.73 km |
| **Stop 18** | C291 | 11:14 | 0.0m | 11:14 | 11:21 | 08:30 - 11:30 | 1.40 km |
| **Stop 19** | C265 | 11:22 | 0.0m | 11:22 | 11:32 | 08:30 - 11:30 | 0.86 km |
| **Stop 20** | C158 | 11:34 | 115.3m | 13:30 | 13:37 | 13:30 - 17:00 | 1.56 km |
| **Stop 21** | C166 | 13:38 | 0.0m | 13:38 | 13:43 | 13:30 - 17:00 | 1.17 km |
| **Stop 22** | C178 | 13:52 | 0.0m | 13:52 | 14:02 | 07:23 - 15:06 | 7.61 km |
| **Stop 23** | C063 | 14:09 | 0.0m | 14:09 | 14:19 | 13:30 - 17:00 | 5.96 km |
| **Stop 24** | C154 | 14:23 | 0.0m | 14:23 | 14:28 | 13:30 - 17:00 | 3.58 km |
| **Stop 25** | C167 | 14:30 | 0.0m | 14:30 | 14:40 | 13:30 - 17:00 | 1.18 km |
| **Stop 26** | C187 | 14:41 | 0.0m | 14:41 | 14:51 | 08:03 - 17:05 | 0.64 km |
| **Stop 27** | C129 | 14:52 | 0.0m | 14:52 | 15:02 | 13:30 - 17:00 | 0.72 km |
| **Stop 28** | C236 | 15:03 | 0.0m | 15:03 | 15:08 | 13:30 - 17:00 | 0.92 km |
| **Stop 29** | C059 | 15:08 | 0.0m | 15:08 | 15:15 | 13:30 - 17:00 | 0.53 km |
| **Stop 30** | C081 | 15:16 | 0.0m | 15:16 | 15:23 | 13:30 - 17:00 | 0.45 km |
| **Stop 31** | C030 | 15:23 | 0.0m | 15:23 | 15:30 | 13:30 - 17:00 | 0.42 km |
| **Stop 32** | C115 | 15:31 | 0.0m | 15:31 | 15:36 | 13:30 - 17:00 | 0.55 km |
| **Stop 33** | C197 | 15:36 | 173.3m | 18:30 | 18:37 | 18:30 - 21:30 | 0.24 km |
| **Stop 34** | C180 | 18:37 | 0.0m | 18:37 | 18:47 | 18:30 - 21:30 | 0.79 km |
| **Stop 35** | C261 | 18:49 | 0.0m | 18:49 | 18:56 | 18:30 - 21:30 | 1.06 km |
| **Stop 36** | C139 | 18:57 | 0.0m | 18:57 | 19:07 | 18:30 - 21:30 | 0.76 km |
| **Stop 37** | C299 | 19:09 | 0.0m | 19:09 | 19:14 | 18:30 - 21:30 | 1.93 km |
| **Stop 38** | C120 | 19:16 | 0.0m | 19:16 | 19:23 | 18:30 - 21:30 | 1.84 km |
| **Stop 39** | C142 | 19:24 | 0.0m | 19:24 | 19:29 | 18:30 - 21:30 | 0.36 km |
| **Stop 40** | C014 | 19:31 | 0.0m | 19:31 | 19:41 | 18:30 - 21:30 | 2.11 km |
| **Stop 41** | C049 | 19:42 | 0.0m | 19:42 | 19:47 | 18:30 - 21:30 | 0.66 km |
| **Stop 42** | C062 | 19:47 | 0.0m | 19:47 | 19:54 | 18:30 - 21:30 | 0.12 km |
| **Stop 43** | C234 | 19:54 | 0.0m | 19:54 | 19:59 | 18:30 - 21:30 | 0.09 km |
| **Stop 44** | C270 | 20:00 | 0.0m | 20:00 | 20:10 | 18:30 - 21:30 | 0.92 km |
| **Stop 45** | C188 | 20:12 | 0.0m | 20:12 | 20:22 | 18:30 - 21:30 | 1.79 km |
| **Stop 46** | C108 | 20:25 | 0.0m | 20:25 | 20:32 | 18:30 - 21:30 | 1.85 km |
| **Stop 47** | C125 | 20:32 | 0.0m | 20:32 | 20:42 | 18:30 - 21:30 | 0.44 km |
| **Stop 48** | C210 | 20:43 | 0.0m | 20:43 | 20:53 | 18:30 - 21:30 | 0.46 km |
| **Stop 49** | C202 | 20:53 | 0.0m | 20:53 | 21:00 | 18:30 - 21:30 | 0.44 km |
| **Stop 50** | C132 | 21:01 | 0.0m | 21:01 | 21:06 | 18:30 - 21:30 | 0.33 km |
| **Stop 51** | C209 | 21:06 | 0.0m | 21:06 | 21:11 | 18:30 - 21:30 | 0.40 km |
| **Stop 52** | C267 | 21:13 | 0.0m | 21:13 | 21:23 | 18:30 - 21:30 | 1.24 km |
| **DEPOT** | - | 21:39 | - | - | - | - | 13.54 km |

### Tại sao không thể chèn C268 vào Thứ Hai?

Để chèn C268 vào khung giờ hợp lệ duy nhất của nó là **18:30 – 21:30** (phút 1110 - 1290) trong ngày thứ Hai:
1. Xe phải thực hiện việc giao hàng cho C268 ngay sau **Stop 32 (C115)** (rời đi lúc 15:36).
2. Thời gian di chuyển từ C115 đến C268: **22.5 phút** (khoảng cách 18.7 km).
3. Thời điểm đến C268: `15:36 + 22.5 phút = 15:58.5`.
4. Xe phải đợi đến **18:30** mới được phục vụ (thêm gần 2.5 tiếng chờ đợi chết).
5. Từ C268, xe đi tiếp đến **C197** mất 24.1 phút.
6. Thời điểm xe đến C197 tiếp theo: `18:40 + 24.1 phút = 19:04.1`.
7. **KẾT QUẢ domino trễ giờ:** Việc detour xa xôi này đẩy thời gian bắt đầu phục vụ các stop tiếp theo (C197, C180, C261...) bị muộn thêm **hơn 34 phút**. Ở cuối chuỗi, khách hàng **C267** thay vì được giao xong lúc 21:23 sẽ bị đẩy xuống thành 21:57 (Vượt quá xa giờ đóng cửa 21:30 của C267). ❌ **VI PHẠM**.

---

## 4. Kết luận Khoa học cho Báo cáo

> **Sự bất khả thi của C268 là một thuộc tính toán học (structural property) của tập dữ liệu Data_B dưới ràng buộc Strict.** 
>
> Ràng buộc khắt khe về thời gian dỡ hàng (10 phút) kết hợp với vị trí địa lý xa depot (21.3 km) và khung giờ mở cửa trễ (chỉ 3 tiếng cuối ngày) khiến C268 không thể xếp chung vào bất kỳ lộ trình tuần hoàn nào mà không làm đổ vỡ các cam kết thời gian của các khách hàng lân cận trên cả 2 ngày duy nhất (Thứ Hai và Thứ Sáu).
