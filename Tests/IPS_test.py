import time
from OxfordMagLab2000.General import Manager
from OxfordMagLab2000.OxfordCryostat import OxfordIPS

rm = Manager.Manager()
IPS = OxfordIPS.OxfordIPS(rm, GPIB_adress='GPIB0::25::INSTR', ISOBUS_master=True)
print(IPS.identity)
print(IPS.last_queried_status)
print(IPS.last_decodified_status)
print(IPS.extended_resolution)
print(IPS.output_current)
print(IPS.output_voltage)
print(IPS.output_field)
print(IPS.current_set_point)
print(IPS.field_set_point)
print(IPS.current_sweep_rate)
print(IPS.field_sweep_rate)
print(IPS.magnet_current)
print(IPS.persistent_current)
print(IPS.persistent_field)
print(IPS.trip_current)
print(IPS.trip_field)
print(IPS.switch_heater_current)
print(IPS.software_voltage_limit)
print(IPS.safe_current_negative_limit)
print(IPS.safe_current_positive_limit)
print(IPS.lead_resistance)
print(IPS.magnet_inductance)
IPS.set_output_current_display()
time.sleep(10)
IPS.set_output_voltage_display()
time.sleep(10)
IPS.set_output_field_display()
time.sleep(10)
IPS.set_current_set_point_display()
time.sleep(10)
IPS.set_field_set_point_display()
time.sleep(10)
IPS.set_current_sweep_rate_display()
time.sleep(10)
IPS.set_field_sweep_rate_display()
time.sleep(10)
IPS.set_magnet_current_display()
time.sleep(10)
IPS.set_persistent_current_display()
time.sleep(10)
IPS.set_persistent_field_display()
time.sleep(10)
IPS.set_trip_current_display()
time.sleep(10)
IPS.set_trip_field_display()
time.sleep(10)
IPS.set_switch_heater_current_display()
time.sleep(10)
IPS.set_software_voltage_limit_display()
time.sleep(10)
IPS.set_safe_current_negative_limit_display()
time.sleep(10)
IPS.set_safe_current_positive_limit_display()
time.sleep(10)
IPS.set_lead_resistance_display()
time.sleep(10)
IPS.set_magnet_inductance_display()
time.sleep(10)
IPS.set_field_set_point_display()
time.sleep(10)
IPS.set_target_field(+1)
IPS.set_activity(hold = False, to_set_point = True)
time.sleep(10)
IPS.set_target_field(0)
time.sleep(10)
IPS.set_target_field(-1)
time.sleep(10)
IPS.set_activity(hold = False, to_zero = True)
IPS.set_target_field(0)
time.sleep(10)
IPS.close()