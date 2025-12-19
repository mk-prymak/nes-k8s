import argparse
import json
import random
import time
from dataclasses import dataclass

import paho.mqtt.client as mqtt


@dataclass(frozen=True)
class Ranges:
    pulse_bpm_min: int = 55
    pulse_bpm_max: int = 120
    spo2_min: int = 90
    spo2_max: int = 100
    sys_min: int = 90
    sys_max: int = 150
    dia_min: int = 55
    dia_max: int = 95


def now_ms() -> int:
    return int(time.time() * 1000)


def make_pulse(device_id: int, rng: random.Random, ranges: Ranges) -> dict:
    return {
        "deviceId": device_id,
        "bpm": rng.randint(ranges.pulse_bpm_min, ranges.pulse_bpm_max),
        "timestamp": now_ms(),
    }


def make_spo2(device_id: int, rng: random.Random, ranges: Ranges) -> dict:
    return {
        "deviceId": device_id,
        "spo2": rng.randint(ranges.spo2_min, ranges.spo2_max),
        "timestamp": now_ms(),
    }


def make_bp(device_id: int, rng: random.Random, ranges: Ranges) -> dict:
    systolic = rng.randint(ranges.sys_min, ranges.sys_max)
    diastolic = min(rng.randint(ranges.dia_min, ranges.dia_max), systolic - 10)
    return {
        "deviceId": device_id,
        "systolic": systolic,
        "diastolic": diastolic,
        "timestamp": now_ms(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=1883)
    parser.add_argument("--devices", type=int, default=5)
    parser.add_argument("--hz", type=float, default=1.0)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--jitter-ms", type=int, default=50)

    args = parser.parse_args()

    if args.hz <= 0:
        print("--hz must be > 0")
        exit(1)

    rng = random.Random(args.seed)
    ranges = Ranges()

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()

    topics = {
        "icu/pulse": make_pulse,
        "icu/bloodPressure": make_bp,
        "icu/spo2": make_spo2,
    }

    interval_s = 1.0 / args.hz

    try:
        while True:
            start = time.time()
            for device_id in range(1, args.devices + 1):
                for topic, fn in topics.items():
                    payload = fn(device_id, rng, ranges)
                    client.publish(topic, json.dumps(payload), qos=0, retain=False)
                    if args.jitter_ms > 0:
                        time.sleep(rng.randint(0, args.jitter_ms) / 1000.0)

            elapsed = time.time() - start
            sleep_for = max(0.0, interval_s - elapsed)
            time.sleep(sleep_for)
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
