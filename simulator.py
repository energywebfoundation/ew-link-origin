import time

import core.input.simulator
from core.commons import logger

meter = core.input.simulator.EnergyMeter()

logger.level = logger.levels.DEBUG
logger.warning("-= Night Compiler =-\n")
logger.info("High verbosity is \033[1mON")

for _ in range(100):
    meter_state = meter.read_state()
    logger.warning("\t-= Device =-")
    logger.info(meter_state.device.serial_number)
    logger.info(meter_state.device.manufacturer)
    logger.info(meter_state.device.model)
    logger.warning("\t-= Access Data =-")
    logger.info(meter_state.access_timestamp)
    logger.info(meter_state.raw)
    logger.warning("\t-= Measurement Data =-")
    logger.info(meter_state.measurement_timestamp)
    logger.info(meter_state.accumulated_power)
    logger.critical("---------------------------------")
    time.sleep(2)
