import json

from azure.core.exceptions import ResourceNotFoundError
from azure.keyvault.secrets import SecretClient, KeyVaultSecret
from azure.identity import DefaultAzureCredential, ChainedTokenCredential

CONFIG_FILE_NAME = "config.json"


def secret_exists(client: SecretClient, name: str) -> bool:
    try:
        client.get_secret(name)
        return True
    except ResourceNotFoundError:
        return False


def get_credentials() -> ChainedTokenCredential:
    return DefaultAzureCredential()


def run_migration():
    with open(CONFIG_FILE_NAME, 'r') as fd:
        config = json.load(fd)
    source_uri = f"https://{config['source-vault-name']}.vault.azure.net"

    destination_uri = f"https://{config['destination-vault-name']}.vault.azure.net"

    credential = get_credentials()
    source_client = SecretClient(vault_url=source_uri, credential=credential)
    dest_client = SecretClient(
        vault_url=destination_uri, credential=credential)

    for secret_name in config['secret-names']:
        secret: KeyVaultSecret = source_client.get_secret(secret_name)

        if not secret_exists(dest_client, secret_name) or dest_client.get_secret(secret_name).value != secret.value:
            print(f'Migrating {secret_name}')
            dest_client.set_secret(secret_name, secret.value)
        else:
            print(f'Skipped: {secret_name}')


if __name__ == '__main__':
    run_migration()
