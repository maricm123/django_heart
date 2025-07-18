import asyncio
from bleak import BleakClient, BleakScanner
import requests

# UUID za Heart Rate Measurement karakteristiku (BLE standard)
HR_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# Tvoj Django API endpoint
API_ENDPOINT = "http://localhost:8000/api/heart-rate/"

# Ako koristiš autentikaciju, dodaj token ovde
HEADERS = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer <your_token_here>"
}


def parse_heart_rate(data: bytearray) -> int:
    # BLE Heart Rate Measurement format
    flags = data[0]
    hr_format = flags & 0x01
    if hr_format == 0:
        return data[1]
    else:
        return int.from_bytes(data[1:3], byteorder="little")


async def main():
    print("Skeniram BLE uređaje...")
    devices = await BleakScanner.discover()

    print(devices)

    # Pronađi Suunto uređaj po imenu
    # suunto = next((d for d in devices if "Suunto" in d.name), None)
    # if not suunto:
    #     print("Suunto uređaj nije pronađen.")
    #     return

    # print(f"Povezujem se na {suunto.name} ({suunto.address})...")
    SUUNTO_ADDRESS = "0C:8C:DC:14:86:D1"
    WHOOP_ADDRESS = "DD:C6:A3:4F:04:6F"
    async with BleakClient(WHOOP_ADDRESS) as client:
        print("Povezan. Čekam podatke...")

        def handle_hr_data(_, data: bytearray):
            bpm = parse_heart_rate(data)
            print(f"Otkucaji srca: {bpm} bpm")

            payload = {
                "device_id": "WHOOP" + WHOOP_ADDRESS,
                "bpm": bpm
            }

            try:
                response = requests.post(API_ENDPOINT, json=payload, headers=HEADERS)
                if response.status_code != 201:
                    print("Greška prilikom slanja:", response.text)
            except Exception as e:
                print("Greška u HTTP zahtevu:", e)

        await client.start_notify(HR_CHAR_UUID, handle_hr_data)

        # Radi 2 minuta
        await asyncio.sleep(120)
        await client.stop_notify(HR_CHAR_UUID)


if __name__ == "__main__":
    asyncio.run(main())
