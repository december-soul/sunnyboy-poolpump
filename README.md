# sunnyboy-poolpump
a tiny to which reads the actual energy produced from my sunnyboy and switch the pool pump on/off

The idea is to switch the pool pump smarter on and off.
If my inverter from SMA (SunnyBoy) produces a lot of power, then I assume that the sun is shining.

In this case my pool pump should pump the water through my solar tubes to warm it up a bit.

I have connected my pool pump to a WLAN socket which I can control via Tasmota.

It's a quick and dirty solution until I get proper sensors.


'''
python3 sunnyboy-poolpump.py -h
usage: sunnyboy-poolpump.py [-h] [--sunnyboyip SUNNYBOYIP]
                            [--sunnyboypassword SUNNYBOYPASSWORD]
                            [--tasmotaip TASMOTAIP] [--powerlow POWERLOW]
                            [--powerhigh POWERHIGH]

a tiny to which reads the actual energy produced from my sunnyboy and switch
the pool pump on/off

optional arguments:
  -h, --help            show this help message and exit
  --sunnyboyip SUNNYBOYIP
                        use 192.168.1.196 as default
  --sunnyboypassword SUNNYBOYPASSWORD
                        your password of the sunnyboy
  --tasmotaip TASMOTAIP
                        use 192.168.1.84 as default
  --powerlow POWERLOW   the level where the pump switch off
  --powerhigh POWERHIGH
                        the level where the pump switch on
'''
