from google.cloud import bigquery
from tqdm import tqdm
import yaml

import synapseclient
import json


# Initialize the Synapse client and log in
syn = synapseclient.Synapse()
syn.login()

# Construct a BigQuery client object.
client = bigquery.Client(project="htan-dcc")


# Helper functions to get and put ACLs
def get_acl(entity_id):
    """
    Fetch the ACL for a given entity by its ID.

    Parameters:
    - entity_id (str): Synapse ID of the entity.

    Returns:
    - dict: The ACL of the entity.
    """
    uri = f"/entity/{entity_id}/acl"
    return syn.restGET(uri)


def put_acl(entity_id, acl):
    """
    Update the ACL for a given entity by its ID with a new ACL.

    Parameters:
    - entity_id (str): Synapse ID of the entity.
    - acl (dict): New ACL to apply to the entity.
    """
    uri = f"/entity/{entity_id}/acl"
    syn.restPUT(uri, json.dumps(acl))


# Load configuration from the external YAML file
config_file_path = "config.yaml"
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

# Assign values from the YAML config
users = config["users"]
permission_levels = config["permission_levels"]

# Append specific ids to make public from the config file
public_dirs = config["public_dirs"]


# Define public view and registered user download permission RAs
public_view_access = {
    "principalId": users["anyone_on_the_web"],
    "accessType": permission_levels["view"],
}
registered_user_download_access = {
    "principalId": users["all_registered_synapse_users"],
    "accessType": permission_levels["download"],
}

# Define the query to fetch releasable entity IDs
query = """
        WITH released AS (
        SELECT entityId, Component, channel_metadata_synapseId
        FROM `htan-dcc.released.entities`
        )
        SELECT entityId AS syn_public FROM released
        WHERE REGEXP_CONTAINS(Component,
        r'Level3|Level4|Auxiliary|Accessory|Other|MassSpectrometry|RPPA')
        UNION ALL
        SELECT DISTINCT channel_metadata_synapseId AS syn_public FROM released
        WHERE channel_metadata_synapseId IS NOT NULL
        """

print("Listing releasable entities...")

# Execute the query and fetch the results
results = client.query(query).result()

print(results)

# Extract the entity IDs from the results

entity_ids = [row["syn_public"] for row in results]
entity_ids.append(public_dirs)

# Subset for testing
entity_ids = entity_ids[:5]

print(f"Ready to make {len(entity_ids)} entities public...")

proceed = input("Do you want to proceed? (y/n): ")
if proceed.lower() == "y":
    print(f"Making {len(entity_ids)} entities public...")
else:
    print("Exiting...")
    exit()

for e in (pbar := tqdm(entity_ids)):

    # Update the progress bar with current entity
    pbar.set_description(f"{e}")

    # Fetch the current ACL for the entity
    current_acl = get_acl(e)
    custom_acl = current_acl

    # Add public view and registered user download permissions
    custom_acl["resourceAccess"].append(public_view_access)
    custom_acl["resourceAccess"].append(registered_user_download_access)

    # Set the ACL on the entity
    put_acl(e, custom_acl)

print("Done!")
