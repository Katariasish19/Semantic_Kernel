from azure.data.tables import TableServiceClient, TableClient
from azure.core.credentials import AzureNamedKeyCredential
import json

account_name = "your-account-name"
account_key = "your-account-key"
table_name = "your-table-name"

credential = AzureNamedKeyCredential(account_name, account_key)

service_client = TableServiceClient(
    endpoint=f"https://{account_name}.table.core.windows.net/",
    credential=credential
)

table_client = TableServiceClient.from_connection_string(
    f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
).get_table_client(table_name)

contract_data = {
    "contractType": "Sale",
    "customer": "John Doe",
    "amount": 1000.00
}

entity = {
    "PartitionKey": "2024-07-30",
    "RowKey": "SESSION123456",
    "ContractJSON": json.dumps(contract_data)
}

table_client.create_entity(entity)

print("Entity inserted successfully.")

retrieved_entity = table_client.get_entity(
    partition_key="2024-07-30",
    row_key="SESSION123456"
)

print("Retrieved entity:")
print(f"PartitionKey: {retrieved_entity['PartitionKey']}")
print(f"RowKey: {retrieved_entity['RowKey']}")
print(f"ContractJSON: {retrieved_entity['ContractJSON']}")

retrieved_contract = json.loads(retrieved_entity['ContractJSON'])
print("Retrieved contract data:")
print(retrieved_contract)




