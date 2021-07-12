import argparse
import asyncio
import logging
import os
import sys
import time

from sma_sunnyboy import *
from tasmotadevicecontroller import TasmotaDevice
from tasmotadevicecontroller import tasmota_types as t

parser = argparse.ArgumentParser(description='a tiny tool which reads the actual energy produced from my sunnyboy and switch the pool pump on/off')
parser.add_argument('--sunnyboyip', default="192.168.1.196", dest="sunnyboyip", help="IP of the sunnyboy solar converter. (default 192.168.1.196)")
parser.add_argument('--sunnyboypassword', default="", dest="sunnyboypassword", help="your password of the sunnyboy. (default empty)")
parser.add_argument('--tasmotaip', default="192.168.1.84", dest="tasmotaip", help="IP of the powerswitch. (default 192.168.1.84)")
parser.add_argument('--powerlow', default=500, dest="powerlow", type=int, help="the level where the pump switch off. (default 500)")
parser.add_argument('--powerhigh', default=1000, dest="powerhigh", type=int, help="the level where the pump switch on. (default 1000)")
parser.add_argument('--powertoggel', default=800, dest="powertoggel", type=int, help="the level where the pump toggel on/off. (default 800)")
args = parser.parse_args()

file_handler = logging.FileHandler(filename='SunnyBoy-PoolPump.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=handlers
)

log = logging.getLogger('Sunnyboy-PoolPump')

sma_address = args.sunnyboyip  # address of SMA
password = args.sunnyboypassword  # your user password
right = Right.USER  # the connexion level
tasmota_address = args.tasmotaip
tasmota_state = t.PowerType.OFF
sma_low = args.powerlow
sma_toggel = args.powertoggel
sma_toggel_time_off = 1  # how often we count until we switch the pump off
sma_toggel_time_on = 5   # how often we count until we switch the pump on
sma_high = args.powerhigh


async def pump(state):
    device = await TasmotaDevice.connect(tasmota_address)
    await device.setPower(state)
    sound(state)


def sound(state):
    duration = 0.1  # seconds
    if state == t.PowerType.OFF:
        freq = 400  # Hz
    else:
        freq = 800  # Hz

    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))


def getPumpState():
    log.info("get pump state")
    device = TasmotaDevice.connect(tasmota_address)
    current_state = device.getPower()
    tasmota_state = t.PowerType.ON if current_state else t.PowerType.OFF
    print(type(tasmota_state))
    print("current state {}".format(tasmota_state))
    return tasmota_state


log.info("init connection to sunnyboy")
client = WebConnect(sma_address, right, password)
client.auth()
loop = asyncio.get_event_loop()

toggel_count = 0
while True:
    # log.info("request power")
    pow_current = client.get_value(Key.power_current)
    if pow_current == None:
        log.info("timeout while connect to sma_sunnyboy")
        # loop.run_until_complete(pump(t.PowerType.OFF))
        time.sleep(1 * 60)
        log.info("reinit connection to sunnyboy")
        client.logout()
        client = WebConnect(sma_address, right, password)
        client.auth()
        continue

    log.info("currently the sunnyboy produce {} W".format(pow_current))
    if pow_current > sma_high and tasmota_state == t.PowerType.OFF:
        log.info("Limit value reached, turn pump on ++++++++++++++++++")
        loop.run_until_complete(pump(t.PowerType.ON))
        tasmota_state = t.PowerType.ON
        toggel_count = 0
    elif pow_current < sma_low and tasmota_state == t.PowerType.ON:
        log.info("Limit value reached, turn pump off -----------------")
        loop.run_until_complete(pump(t.PowerType.OFF))
        tasmota_state = t.PowerType.OFF
        toggel_count = 0
    elif pow_current > sma_toggel and pow_current < sma_high:
        toggel_count += 1
        # log.info("Toggel {}".format(toggel_count))
        if tasmota_state == t.PowerType.OFF:
            if toggel_count > sma_toggel_time_on:
                log.info("Toggel Limit value reached, turn pump on ++++++++++++++++++{}".format(toggel_count))
                loop.run_until_complete(pump(t.PowerType.ON))
                tasmota_state = t.PowerType.ON
                toggel_count = 0
        else:
            if toggel_count > sma_toggel_time_off:
                log.info("Toggel Limit value reached, turn pump off -----------------{}".format(toggel_count))
                loop.run_until_complete(pump(t.PowerType.OFF))
                tasmota_state = t.PowerType.OFF
                toggel_count = 0


    time.sleep(1 * 60)  # sleep 1 min
client.logout()
