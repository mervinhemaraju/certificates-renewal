from kink import di
from utils.constants import SECRETS_MAIN_PROJECT_NAME, SECRETS_MAIN_CONFIG


def extract_secret(name):
    '''
        This function extracts a secret from the DI secrets using the provided name.
    '''
    return di["secrets"].get(
        project=SECRETS_MAIN_PROJECT_NAME,
        config=SECRETS_MAIN_CONFIG,
        name=name,
    ).value["raw"]