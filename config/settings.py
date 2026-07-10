import os
from dataclasses import dataclass

@dataclass(frozen=True)
class SettingsConfig:
    max_days: int = 7
    vehicle_capacity: float = 1e9  # Extremely large as capacity is not strictly constrained, but modelable
    vehicle_speed: float = 50.0    # Speed limit 50 km/h
    depot_id: str = "DEPOT"
    # Thời điểm xe xuất phát từ kho mỗi ngày (đơn vị: phút tính từ 00:00).
    # Mặc định = 480.0 (08:00 AM). Giá trị này được suy ra từ dữ liệu:
    # khung giờ sớm nhất trong toàn bộ dataset là 07:00 (C140, Thứ Năm),
    # nên 08:00 AM là mốc xuất phát an toàn và thực tế.
    # Với dataset mới có giờ mở cửa sớm hơn, hãy điều chỉnh giá trị này.
    depot_start_time: float = 480.0  # 08:00 AM

def get_settings() -> SettingsConfig:
    return SettingsConfig()
