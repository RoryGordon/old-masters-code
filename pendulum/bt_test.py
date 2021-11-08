
import bluetooth

print("Scanning for devices:")

devices = bluetooth.discover_devices(lookup_names=True, lookup_class=False)

num_of_devices = len(devices)

print(f"{num_of_devices} devices found")

for addr, name in devices:
    print("\n\tDevice:")
    print(f"\tDevice name: {name}")
    print(f"\t MAC adress: {addr}")
    #print(f"\t      class: {device_class}")
'''

import pexpect
import sys
DEVICE = "00:A0:50:CF:62:CD"   # address of your device
if len(sys.argv) == 2:
  DEVICE = str(sys.argv[1])
# Run gatttool interactively.
child = pexpect.spawn("gatttool -I")

# Connect to the device.
print("Connecting to:"),
print(DEVICE)
NOF_REMAINING_RETRY = 3
while True:
  try:
    child.sendline("connect {0}".format(DEVICE))
    child.expect("Connection successful", timeout=5)
  except pexpect.TIMEOUT:
    NOF_REMAINING_RETRY = NOF_REMAINING_RETRY-1
    if (NOF_REMAINING_RETRY>0):
      print("timeout, retry...")
      continue
    else:
      print("timeout, giving up.")
      break
  else:
    print("Connected!")
    break
'''