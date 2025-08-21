from kink import di
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend


def extract_secret(secret, project, key):
    return secret.get(
        project=project,
        config="prd",
        name=key,
    ).value["raw"]


def check_certificate_expiry(certficate: str, days_before_expiration: int = 30):
    """
    Check if certificate exists and needs renewal
    """

    try:
        # Parse certificate
        cert = x509.load_pem_x509_certificate(certficate, default_backend())

        # Calculate days until expiry
        expiry_date = cert.not_valid_after
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
