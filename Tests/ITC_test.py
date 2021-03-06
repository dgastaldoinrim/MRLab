import time
from OxfordMagLab2000.General import Manager
from OxfordMagLab2000.OxfordCryostat import OxfordITC

rm = Manager.Manager()
ITC = OxfordITC.OxfordITC(rm, GPIB_adress='GPIB0::24::INSTR')
print(ITC.identity)
print(ITC.last_queried_status)
print(ITC.last_decodified_status)
print(ITC.temperature_set_point)
print(ITC.sensor_1_temperature)
print(ITC.sensor_2_temperature)
print(ITC.sensor_3_temperature)
print(ITC.heater_operating_point)
print(ITC.needle_valve_operating_point)
print(ITC.P_term)
print(ITC.I_term)
print(ITC.D_term)
print(ITC.heater_automatic_control)
print(ITC.needle_valve_automatic_control)
print(ITC.auto_PIDS_mode)
print(ITC.heater_controlling_sensor)
print(ITC.maximum_heater_output)
print(ITC.sweep_step)
ITC.set_temperature_set_point_display()
time.sleep(10)
ITC.set_temperature_set_point(320)
print(ITC.temperature_set_point)
time.sleep(10)
ITC.set_temperature_set_point(0)
print(ITC.temperature_set_point)
time.sleep(10)
ITC.set_sensor_1_temperature_display()
print(ITC.sensor_1_temperature)
time.sleep(10)
ITC.set_sensor_2_temperature_display()
print(ITC.sensor_2_temperature)
time.sleep(10)
ITC.set_sensor_3_temperature_display()
print(ITC.sensor_3_temperature)
time.sleep(10)
ITC.set_heater_operating_point_display()
ITC.set_heater_controlling_sensor(1)
print(ITC.heater_controlling_sensor)
time.sleep(10)
ITC.set_heater_controlling_sensor(2)
print(ITC.heater_controlling_sensor)
time.sleep(10)
ITC.set_heater_controlling_sensor(3)
print(ITC.heater_controlling_sensor)
time.sleep(10)
ITC.set_heater_controlling_sensor(1)
ITC.set_heater_operating_point_display()
print(ITC.heater_operating_point)
ITC.set_manual_heater(10)
print(ITC.heater_operating_point)
ITC.set_manual_heater(0)
print(ITC.heater_operating_point)
ITC.set_needle_valve_operating_point_display()
print(ITC.needle_valve_operating_point)
ITC.set_manual_gas_flow(45)
print(ITC.needle_valve_operating_point)
time.sleep(60)
ITC.set_manual_gas_flow(0)
print(ITC.needle_valve_operating_point)
time.sleep(60)
ITC.set_P_term_display()
print(ITC.P_term)
ITC.set_P_control_term(25)
print(ITC.P_term)
time.sleep(10)
ITC.set_P_control_term(50)
print(ITC.P_term)
time.sleep(10)
ITC.set_I_term_display()
print(ITC.I_term)
ITC.set_I_control_term(30)
print(ITC.I_term)
time.sleep(10)
ITC.set_I_control_term(1)
print(ITC.I_term)
time.sleep(10)
ITC.set_D_term_display()
print(ITC.D_term)
ITC.set_D_control_term(30)
print(ITC.D_term)
time.sleep(10)
ITC.set_D_control_term(0.5)
print(ITC.D_term)
time.sleep(10)
ITC.set_sensor_1_temperature_display()
ITC.close()
