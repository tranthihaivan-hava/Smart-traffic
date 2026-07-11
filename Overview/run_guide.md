# Hướng Dẫn Chạy Toàn Bộ Hệ Thống (End-to-End Workflow)

Tài liệu này ghi lại quy trình chuẩn (SOP) để chạy lại toàn bộ Kiến trúc Two-Phase BOMA từ đầu đến cuối. Sử dụng quy trình này mỗi khi bạn nhận được một bộ dữ liệu (Dataset) khách hàng hoặc bản đồ mới.

---

## Bước 1: Thay Dữ liệu & Xóa Lịch sử Cũ
Khi có dữ liệu mới, bạn cần xóa bỏ các dấu vết học tập cũ để AI (Optuna) không bị nhầm lẫn.

1. Ghi đè file `locations.csv` và `time_windows.csv` mới vào thư mục `Data_B/`.
2. Xóa file Database cũ: `Data_B/boma_two_phase.db`
3. Xóa file Checkpoint cũ: `Data_B/final_checkpoint.json`

---

## Bước 2: Giai đoạn 1 - Tìm Trọng số Vàng (Phase 1)
Mở Terminal ở thư mục gốc của dự án (`SMART-TRAFFIC`) và chạy lệnh sau để Optuna bắt đầu quá trình huấn luyện tìm trọng số:

```bash
python3 runners/train_hga_bayesian.py
```
*Ghi chú: Quá trình này sẽ mất một khoảng thời gian. Optuna sẽ lưu kết quả 4 trọng số hoàn hảo nhất vào file `.db`.*

---

## Bước 3: Giai đoạn 2 - Nội suy ra Lộ trình (Phase 2)
Sau khi có "Trọng số vàng", chạy HGA quy mô lớn để sinh ra lịch trình tối ưu nhất:

```bash
python3 runners/run_benchmark.py
```
*Ghi chú: HGA sẽ chạy 30 thế hệ và lưu lộ trình tốt nhất vào file `final_checkpoint.json`.*

---

## Bước 4: Cứu hộ & Đóng băng kết quả
Chạy thuật toán Local Search (Repair Operator) để "cứu" nốt những đơn hàng bị rớt (nếu có) và đóng băng kết quả cuối cùng để vẽ biểu đồ:

```bash
python3 export_presentation.py
```
*Ghi chú: Lệnh này sẽ tạo ra file `Overview/presentation_result.txt` (định dạng JSON). Đây là Single Source of Truth cho toàn bộ báo cáo.*

---

## Bước 5: Xuất Báo cáo & Vẽ Biểu đồ (Nhất quán 100%)
Chạy lần lượt 4 lệnh dưới đây để tự động tạo Bảng Markdown, vẽ Biểu đồ và kiểm tra tính hợp lệ của Toán học:

```bash
# 1. Sinh bảng lịch trình chi tiết Markdown
python3 runners/generate_detailed_schedule.py

# 2. Sinh các biểu đồ Timeline, Bản đồ, Pie chart...
python3 Overview/visualize/generate_final_visuals.py

# 3. Vẽ biểu đồ so sánh các thuật toán (Greedy vs HGA)
python3 Overview/visualize/plot_metrics_comparison.py

# 4. Chạy Validator khắt khe để đảm bảo 0 có lỗi Toán học/Time Windows
python3 utils/strict_validator.py
```

🎉 **Hoàn thành!** Toàn bộ file kết quả, biểu đồ và bảng biểu trong thư mục `Overview/` lúc này đã được cập nhật mới và khớp nhau 100%. Bạn có thể dùng chúng để báo cáo.
