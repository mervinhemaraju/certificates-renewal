from kink import di
from datetime import datetime
import OpenSSL
import time


def extract_secret(secret, project, key):
    return secret.get(
        project=project,
        config="prd",
        name=key,
    ).value["raw"]


def check_certificate_expiry(certificate, days_before_expiration: int = 30):
    """
    Check if certificate exists and needs renewal using pyOpenSSL
    """
    try:
        # Parse certificate
        cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)

        # Get expiry date
        expiry_bytes = cert.get_notAfter()
        expiry_str = expiry_bytes.decode("ascii")

        # Parse the date string (format: YYYYMMDDHHMMSSZ)
        expiry_date = datetime.strptime(expiry_str, "%Y%m%d%H%M%SZ")

        # Calculate days until expiry
        days_remaining = (expiry_date - datetime.now()).days

        print(
            f"Current certificate expires on {expiry_date}. Days remaining: {days_remaining}"
        )

        # Check if renewal is needed
        needs_renewal = days_remaining <= days_before_expiration

        return needs_renewal, days_remaining

    except Exception as e:
        print(f"Error checking certificate: {str(e)}")
        return True, 0
