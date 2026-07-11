# Hướng dẫn chi tiết: Cách HGA và Solomon I1 chèn lộ trình

Để hiểu rõ tại sao HGA lại cần Solomon I1, chúng ta hãy cùng xem xét một ví dụ "đồ chơi" (Toy Example) cực kỳ dễ hiểu với **5 Khách hàng** và xe tải có **2 Ngày** làm việc.

## 1. Dữ liệu giả định (Toy Data)
- **Depot (D)**: Nơi xuất phát.
- **Khách hàng**: C1, C2, C3, C4, C5
- Giả sử HGA (Thuật toán Di truyền) đã lai ghép và sinh ra một chuỗi Bộ Gen (Chromosome) theo thứ tự:
  👉 **`Chromosome = [C1, C4, C2, C5, C3]`**

Bây giờ, HGA giao chuỗi này cho **Solomon I1** và bảo: *"Lắp ráp đi!"*

---

## 2. Quá trình Lắp ráp (Decoding / Insertion)

Solomon I1 chuẩn bị sẵn 2 chiếc xe trống trơn cho 2 ngày:
- Ngày 1: `[D, D]`
- Ngày 2: `[D, D]`

### Bước 1: Lấy gen đầu tiên -> `C1`
- Solomon thử chèn `C1` vào Ngày 1. Chỉ có 1 khe hở duy nhất là chèn vào giữa `[D, D]`.
- Lộ trình thử nghiệm: `[D, C1, D]`.
- **Kiểm tra:** C1 giao kịp giờ. Xăng tốn 20km.
- **Quyết định:** Gắn vĩnh viễn C1 vào Ngày 1.
- **Trạng thái:** Ngày 1 = `[D, C1, D]`

### Bước 2: Lấy gen tiếp theo -> `C4`
- Solomon nhìn vào Ngày 1 đang là `[D, C1, D]`. Nó thấy có **2 khe hở** để chèn C4:
  - Khe số 1 (Trước C1): `[D, C4, C1, D]`
  - Khe số 2 (Sau C1): `[D, C1, C4, D]`
- **Tính toán:** Nó tính toán $c_1$ (Chi phí đội lên của quãng đường) cho cả 2 khe và phát hiện khe số 2 tốn ít xăng hơn và C4 không bị trễ giờ.
- **Quyết định:** Chèn C4 vào khe số 2.
- **Trạng thái:** Ngày 1 = `[D, C1, C4, D]`

### Bước 3: Lấy gen tiếp theo -> `C2` (Bắt đầu kịch tính)
- Ngày 1 đang là `[D, C1, C4, D]`. Solomon thử chèn `C2` vào **3 khe hở**:
  - `[D, C2, C1, C4, D]` ❌ **LỖI:** Giao C2 xong chạy tới C1 thì C1 đã đóng cửa (Trễ giờ Time Window).
  - `[D, C1, C2, C4, D]` ❌ **LỖI:** Giao C1 xong chạy tới C2 thì C2 đóng cửa.
  - `[D, C1, C4, C2, D]` ❌ **LỖI:** Quá tải trọng xe tải.
- Ngày 1 đã kẹt cứng! Solomon không hoảng hốt, nó chuyển sang **Ngày 2** (`[D, D]`).
- Nó chèn C2 vào Ngày 2: `[D, C2, D]`. Hoàn toàn hợp lệ!
- **Trạng thái:** Ngày 1 = `[D, C1, C4, D]` | Ngày 2 = `[D, C2, D]`

### Bước 4: Lấy gen tiếp theo -> `C5`
- Solomon thử quét khe hở ở **cả Ngày 1 và Ngày 2**.
- Nó nhận thấy chèn C5 vào sau C4 ở Ngày 1 thì bị quá giờ. Chèn C5 vào sau C2 ở Ngày 2 thì vừa khít và ít tốn xăng nhất.
- **Quyết định:** Chèn C5 vào Ngày 2.
- **Trạng thái:** Ngày 1 = `[D, C1, C4, D]` | Ngày 2 = `[D, C2, C5, D]`

### Bước 5: Lấy gen cuối cùng -> `C3`
- Solomon thử chèn C3 vào mọi khe hở của cả Ngày 1 và Ngày 2.
- **Tình huống:** Bất chấp chèn vào đâu, C3 cũng đều làm trễ giờ của các khách hàng phía sau nó. Không có bất kỳ vị trí nào hợp lệ.
- **Quyết định:** Đánh rớt C3 (Unserved).

---

## 3. Tổng kết & Chấm điểm (Fitness)
Sau khi Solomon I1 thi công xong chuỗi `[C1, C4, C2, C5, C3]`, nó gửi bản báo cáo kết quả về lại cho hệ thống HGA:
- **Lộ trình cuối:** 
  - Ngày 1: `[D, C1, C4, D]`
  - Ngày 2: `[D, C2, C5, D]`
- **Rớt khách:** 1 người (C3)
- **Tổng quãng đường:** 140 km.

HGA (Cái máy Xổ số) cầm lấy báo cáo này, chấm điểm (Fitness) cho chuỗi Gen đó. Sau đó, HGA sẽ sinh ra một chuỗi Gen mới tinh (ví dụ `[C3, C2, C1, C5, C4]`) và bắt Solomon I1 lắp ráp lại từ đầu để xem chuỗi mới có cứu được ông khách C3 không.

**Đó chính là nguyên lý vĩ đại của Order-Based Insertion Heuristic (HGA + Solomon I1)!**
