from kink import di
from certbot._internal import main as certbot_main

# from cryptography.x509.oid import NameOID
# from cryptography.hazmat.primitives import hashes, serialization
# from cryptography.hazmat.primitives.asymmetric import rsa
from functions import check_certificate_expiry, extract_secret
from di import main_injection

# Configuration
DOMAIN = "mervinhemaraju.com"  # Your domain
EMAIL = "mervinhemaraju16@gmail.com"  # Your email for Let's Encrypt notifications
DAYS_BEFORE_EXPIRY = 30  # Renew if cert expires in less than 30 days
WORKING_DIRECTORY = "/tmp"  # Activate when using lambda
# WORKING_DIRECTORY = "tmp"
CLOUDFLARE_INI_FILE = f"{WORKING_DIRECTORY}/cloudflare.ini"
EXPECTED_CERT_DIRECTORY = f"{WORKING_DIRECTORY}/live/mervinhemaraju.com"


@main_injection
def main(event, context):
    # TODO(Change print to logging)

    # Get the cloudflare token
    cloudflare_token = extract_secret(
        secret=di["secrets"], project="apps-creds", key="CLOUDFLARE_TERRAFORM_TOKEN"
    )

    # Create the cloudflare.ini file
    with open(CLOUDFLARE_INI_FILE, "w") as f:
        f.write(f"dns_cloudflare_api_token = {cloudflare_token}\n")

    # Get the OCI namespace
    oci_namespace = di["oci_bucket_client"].get_namespace().data

    # TODO(Get the certificate from the oci bucket)
    get_certificates_response = (
        di["oci_bucket_client"]
        .get_object(
            namespace_name=oci_namespace,
            bucket_name="certificates",
            object_name="live/san-mervinhemaraju-com-plagueworks-org/cert.pem",
        )
        .data
    )

    # If certificate doesn't exist, raise error
    if get_certificates_response.status_code != 200:
        raise Exception("Cannot find the certificate file for domain ->")

    # Get the certificate content
    certificate_content = get_certificates_response.content

    # Check whether the certificate is expiring
    needs_renewal, days_remaining = check_certificate_expiry(
        certificate=certificate_content
    )

    # Log info
    print(f"Needs renewwal: {needs_renewal}")

    print(f"Certificate expires in {days_remaining} days. Renewing...")

    # TODO(Add a condition here to check if renewal is needed)
    certbot_args = [
        "certonly",
        "--non-interactive",
        "--agree-tos",
        "--email",
        EMAIL,
        "--dns-cloudflare",
        "--dns-cloudflare-credentials",
        CLOUDFLARE_INI_FILE,
        "--dns-cloudflare-propagation-seconds",
        "30",
        "--preferred-challenges",
        "dns-01",
        "-d",
        "*.mervinhemaraju.com",
        "-d",
        "*.plagueworks.org",
        "--config-dir",
        WORKING_DIRECTORY,
        "--work-dir",
        WORKING_DIRECTORY,
        "--logs-dir",
        WORKING_DIRECTORY,
        # '--force-renewal'  # Force renewal even if cert is valid
    ]

    # Run certbot
    result = certbot_main.main(certbot_args)

    print(result)

    # Read the certificate file
    CERT_FILE = f"{EXPECTED_CERT_DIRECTORY}/cert.pem"

    with open(CERT_FILE, "r") as cert_file:
        new_cert = cert_file.read()

        print(new_cert)

        # Check whether the certificate is expiring
        needs_renewal, days_remaining = check_certificate_expiry(
            certificate=new_cert.encode()
        )

        # Log info
        print(f"New cert needs renewal: {needs_renewal}")

        print(f"New certificate expires in {days_remaining} days.")

    # TODO(Add slack notifications)
