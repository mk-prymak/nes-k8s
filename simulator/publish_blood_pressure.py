import argparse
import json
import random
import time

import paho.mqtt.client as mqtt

from common import DeviceIdentity, base_payload, load_schema, validate_or_raise


def main() -> None:
    parser = argparse.ArgumentParser(description="Blood pressure sensor simulator (single device)")
    parser.add_argument("--host", default="127.0.0.1", help="MQTT host (use port-forward to mosquitto)")
    parser.add_argument("--port", type=int, default=1883, help="MQTT TCP port")
    parser.add_argument("--device-id", required=True, help="Stable device id, e.g. bp-icu-a-bed-3")
    parser.add_argument("--icu-id", required=True, help="ICU identifier, e.g. icu-a")
    parser.add_argument("--bed-id", required=True, help="Bed identifier, e.g. bed-3")
    parser.add_argument("--hz", type=float, default=0.2, help="Samples per second (BP is typically slower)")
    parser.add_argument("--seed", type=int, default=1, help="Random seed for reproducibility")
    parser.add_argument("--jitter-ms", type=int, default=100, help="Random publish jitter (ms)")
    parser.add_argument("--sys-min", type=int, default=90)
    parser.add_argument("--sys-max", type=int, default=150)
    parser.add_argument("--dia-min", type=int, default=55)
    parser.add_argument("--dia-max", type=int, default=95)

    args = parser.parse_args()
    if args.hz <= 0:
        raise SystemExit("--hz must be > 0")

    rng = random.Random(args.seed)
    identity = DeviceIdentity(device_id=args.device_id, icu_id=args.icu_id, bed_id=args.bed_id)
    schema = load_schema("blood_pressure.schema.json")

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(args.host, args.port, keepalive=60)
    client.loop_start()

    interval_s = 1.0 / args.hz
    topic = "icu/bloodPressure"

    try:
        while True:
            start = time.time()
            payload = base_payload(identity)
            systolic = rng.randint(args.sys_min, args.sys_max)
            diastolic = min(rng.randint(args.dia_min, args.dia_max), systolic - 10)
            payload["systolic"] = systolic
            payload["diastolic"] = diastolic
            validate_or_raise(payload, schema)
            client.publish(topic, json.dumps(payload), qos=0, retain=False)

            if args.jitter_ms > 0:
                time.sleep(rng.randint(0, args.jitter_ms) / 1000.0)

            elapsed = time.time() - start
            time.sleep(max(0.0, interval_s - elapsed))
    except KeyboardInterrupt:
        pass
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()


