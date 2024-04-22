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


def make_public(synid):
    registered = syn.getPermissions(synid, "273948") == ["DOWNLOAD", "READ"]
    if registered:
        pass
    else:
        syn.setPermissions(
            synid, "273948", ["DOWNLOAD", "READ"], warn_if_inherits=False
        )
    public = syn.getPermissions(synid, "PUBLIC") == ["READ"]
    if public:
        pass
    else:
        syn.setPermissions(
            synid, principalId="PUBLIC", accessType=["READ"], warn_if_inherits=False
        )


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
        r'Level[34]|Auxiliary|Accessory|Other|MassSpectrometry|RPPA')
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

    make_public(e)


print("Done!")
