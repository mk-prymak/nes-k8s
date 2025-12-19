import time
from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator


CONTRACT_VERSION = 1


@dataclass(frozen=True)
class DeviceIdentity:
    device_id: str
    icu_id: str
    bed_id: str


def now_ms() -> int:
    return int(time.time() * 1000)


def base_payload(identity: DeviceIdentity) -> dict:
    return {
        "contractVersion": CONTRACT_VERSION,
        "deviceId": identity.device_id,
        "icuId": identity.icu_id,
        "bedId": identity.bed_id,
        "timestampMs": now_ms(),
    }


def load_schema(schema_filename: str) -> dict:
    schema_path = Path(__file__).resolve().parent / "contract" / schema_filename
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    import json

    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_or_raise(payload: dict, schema: dict) -> None:
    Draft202012Validator(schema).validate(payload)


