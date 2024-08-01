import asyncio
import argparse
from bleak import BleakScanner
from parser import parse_hex  # Import the parse_hex function
from setup_payload import SetupPayload
from bleak import BleakClient
import hashlib

TARGET_UUID = "0000fff6-0000-1000-8000-00805f9b34fb"
C3_UUID = "64630238-8772-45F2-B87D-748A83218F04"

# ANSI escape codes for colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def match_rid(read_rid, rid):
    # Initialize the SHA-256 hash object
    m = hashlib.sha256()

    # Update the hash object with the RID and the first 2 bytes of read_rid
    m.update(bytearray.fromhex(rid))
    m.update(read_rid[:2])

    # Get the hexadecimal digest of the hash
    digest = m.hexdigest()

    digest_32 = digest[-32:]
    # print(digest_32)
    read_rid = read_rid.hex()
    read_rid =read_rid[-32:]
    # print(read_rid)
    if digest_32 == read_rid:
        return True
    else:
        return False



async def read_c3_characteristic(address, rid=None, timeout=60.0):
    async with BleakClient(address, timeout=timeout) as client:
        try:
            # Check if the device is connected
            is_connected = client.is_connected
            if is_connected:
                print(f"Connected to {address}")

                # Read the C3 characteristic
                c3_value = await client.read_gatt_char(C3_UUID)
                print(f"C3 Characteristic Value: {c3_value.hex()}")

                if rid:
                    rid_length = int(c3_value[3])
                    rid_from_data = c3_value[4:4+rid_length]
                    print(f"Read RID: {rid_from_data.hex()}")

                    # Check if rid matches
                    if match_rid(rid_from_data,rid):
                        print(f"{GREEN}RID Matched!{RESET}")
                    else:
                        print(f"{RED}RID Mismatched!{RESET}")
            else:
                print(f"Failed to connect to {address}")

        except Exception as e:
            print(f"An error occurred: {e}")


async def discover(code):
    async with BleakScanner() as scanner:
        print("Scanning for the following device...")
        # Parse the QR code payload
        setup_payload = SetupPayload.parse(code)
        # Print the details
        setup_payload.p_print()
        vid = setup_payload.vid
        pid = setup_payload.pid
        long_disc = setup_payload.long_discriminator
        short_disc = setup_payload.short_discriminator
        print(f"\nFinding Matter Commissionable devices ...")
        async for bd, ad in scanner.advertisement_data():
            # Check if service_data is present
            if ad.service_data:
                for uuid, data in ad.service_data.items():
                    if uuid == TARGET_UUID:
                        print(f"Matter Device found with Service Data: {data.hex()}")
                        # Decode the service data
                        hex_string = data.hex()
                        try:
                            decoded_values = parse_hex(hex_string)
                            long_discriminator_value = int(decoded_values.get("Discriminator"), 16)
                            short_discriminator_value = int(decoded_values.get("Short Discriminator"), 16)

                            if (long_disc == long_discriminator_value or short_disc == short_discriminator_value):
                                for key, value in decoded_values.items():
                                    print(f"{key}: {value}")
                                print(f"{GREEN}Discriminator Matched!{RESET}")
                                print(f"{GREEN}THE DEVICE IS IN COMMISSIONABLE MODE.{RESET}")

                                if decoded_values.get("Additional Data Flag") == 1:
                                    print(f"Fetching Additional data for Device address: {bd.address}")
                                    return bd.address
                                else:
                                    return

                            else:
                                for key, value in decoded_values.items():
                                    print(f"{key}: {value}")
                                print(f"{RED}Discriminator Mismatched!{RESET}")

                        except ValueError as e:
                            print(f"Error decoding service data: {e}")


async def main(code, rid=None):
    # Discover the device
    device_address = await discover(code)
    if device_address:
        print(f"Found device at address: {device_address}")
        # Read the C3 characteristic from the discovered device
        await read_c3_characteristic(device_address, rid)

async def run_with_timeout(code, timeout, rid=None):
    try:
        await asyncio.wait_for(main(code, rid), timeout)
    except asyncio.TimeoutError:
        print(f"{RED}Program timed out after {timeout} seconds.{RESET}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for BLE devices and decode service data.")
    parser.add_argument("code", type=str, help="The QR/manual code payload to be parsed.")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout for the program in seconds.")
    parser.add_argument("--rid", type=str, help="Rotational Device ID to match against.")
    args = parser.parse_args()

    asyncio.run(run_with_timeout(args.code, args.timeout, args.rid))


