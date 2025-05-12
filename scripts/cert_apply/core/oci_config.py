import oci
from utils.secrets_extraction import extract_secret

def generate_cross_config(
    account_name: str,
    region: str,
) -> dict:
    #  Retrieve account info from secrets
    user_id = extract_secret(name=f"OCI_{account_name.upper()}_USER_OCID")
    tenancy_id = extract_secret(name=f"OCI_{account_name.upper()}_TENANCY_OCID")
    key_content = extract_secret(name=f"OCI_{account_name.upper()}_PRIVATE_KEY")
    fingerprint = extract_secret(name=f"OCI_{account_name.upper()}_FINGERPRINT")

    # Return the config
    return {
        "user": user_id,
        "key_content": key_content,
        "fingerprint": fingerprint,
        "tenancy": tenancy_id,
        "region": region,
    }

def generate_local_config_and_signer():
    return {'region': 'uk-london-1'}, oci.auth.signers.InstancePrincipalsSecurityTokenSigner()