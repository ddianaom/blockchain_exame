from datetime import datetime
from flask import abort, make_response

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))

PATIENT = {
    "Larissa": {
        "fname": "Larissa",
        "lname": "Rock",
        "timestamp": get_timestamp(),
    },
    "Diana": {
        "fname": "Diana",
        "lname": "Samba",
        "timestamp": get_timestamp(),
    },
    "Fábio": {
        "fname": "Fábio",
        "lname": "Ragge",
        "timestamp": get_timestamp(),
    }
}

def read_all():
    return list(PATIENT.values())

def create(patient):
    lname = patient.get("lname")
    fname = patient.get("fname", "")

    if lname and lname not in PATIENT:
        PATIENT[lname] = {
            "lname": lname,
            "fname": fname,
            "timestamp": get_timestamp(),
        }
        return PATIENT[lname], 201
    else:
        abort(
            406,
            f"Patient with last name {lname} already exists",
        )

def read_one(lname):
    if lname in PATIENT:
        return PATIENT[lname]
    else:
        abort(
            404, f"Patient with last name {lname} not found"
        )

def update(lname, patient):
    if lname in PATIENT:
        PATIENT[lname]["fname"] = patient.get("fname", PATIENT[lname]["fname"])
        PATIENT[lname]["timestamp"] = get_timestamp()
        return PATIENT[lname]
    else:
        abort(
            404,
            f"Patient with last name {lname} not found"
        )

def delete(lname):
    if lname in PATIENT:
        del PATIENT[lname]
        return make_response(
            f"{lname} successfully deleted", 200
        )
    else:
        abort(
            404,
            f"Patient with last name {lname} not found"
        )