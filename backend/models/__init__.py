"""
模型初始化文件
Model initialization file
"""
from backend.models.equipment import Equipment
from backend.models.equipment_category import EquipmentCategory
from backend.models.equipment_time_slot import EquipmentTimeSlot
from backend.models.recurring_reservation import RecurringReservation
# 注意：先导入reservation_history，再导入reservation，避免循环引用问题
from backend.models.reservation_history import ReservationHistory
from backend.models.reservation import Reservation

__all__ = [
    'Equipment',
    'Reservation',
    'EquipmentCategory',
    'RecurringReservation',
    'EquipmentTimeSlot',
    'ReservationHistory'
]
