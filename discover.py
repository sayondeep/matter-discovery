import asyncio
import argparse
from bleak import BleakScanner
from parser import parse_hex  # Import the parse_hex function
from setup_payload import SetupPayload

TARGET_UUID = "0000fff6-0000-1000-8000-00805f9b34fb"

# ANSI escape codes for colors
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

async def main(code):
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
                            discriminator_value = int(decoded_values.get("Discriminator"), 16)
                            if(long_disc == discriminator_value):
                                for key, value in decoded_values.items():
                                    print(f"{key}: {value}")
                                print(f"{GREEN}Discriminator Matched!{RESET}")
                                print(f"{GREEN}THE DEVICE IS IN COMMISSIONABLE MODE.{RESET}")

                                return
                            discriminator_value = int(decoded_values.get("Short Discriminator"), 16)
                            if(short_disc == discriminator_value):
                                for key, value in decoded_values.items():
                                    print(f"{key}: {value}")
                                print(f"{GREEN}Discriminator Matched!{RESET}")
                                print(f"{GREEN}THE DEVICE IS IN COMMISSIONABLE MODE.{RESET}")

                                return
                            else:
                                for key, value in decoded_values.items():
                                    print(f"{key}: {value}")
                                print(f"{RED}Discriminator MisMatched!{RESET}")

                        except ValueError as e:
                            print(f"Error decoding service data: {e}")

async def run_with_timeout(code, timeout):
    try:
        await asyncio.wait_for(main(code), timeout)
    except asyncio.TimeoutError:
        print(f"{RED}Program timed out after {timeout} seconds.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for BLE devices and decode service data.")
    parser.add_argument("code", type=str, help="The QR/manual code payload to be parsed.")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout for the program in seconds.")
    args = parser.parse_args()

    asyncio.run(run_with_timeout(args.code, args.timeout))

