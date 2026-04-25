"""VIN utilities.

The MVP keeps VIN decoding as a stub so the app can run before paid/free VIN
services are wired in.
"""


def decode_vin_stub(vin: str | None) -> dict:
    """Return a placeholder VIN decode result."""
    if not vin:
        return {
            "available": False,
            "message": "No VIN supplied. Vehicle identity must come from user-entered year/make/model.",
        }

    return {
        "available": False,
        "vin": vin,
        "message": "VIN decoder not connected yet. Do not infer trim/engine from VIN in MVP.",
    }
