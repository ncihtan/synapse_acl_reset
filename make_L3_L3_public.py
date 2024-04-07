from google.cloud import bigquery
from tqdm import tqdm

import synapseclient
import json

# Initialize the Synapse client and log in
syn = synapseclient.Synapse()
syn.login()

# Construct a BigQuery client object.
client = bigquery.Client(project="htan-dcc")

query = """
    SELECT entityId FROM `htan-dcc.released.entities_v5_1`
    WHERE Component LIKE '%Level3' OR Component LIKE '%Level4'
    LIMIT 20
"""

query_job = client.query(query)  # Make an API request.

# Fetch the results.
results = query_job.result()

entity_ids = []

for row in results:
    entity_ids.append(row["entityId"])

# Define specific resource access for the ACL

# Define users or teams by their principal IDs
principals = {
    "htan_dcc_admins": 3497313,
    "htan_dcc": 3391844,
    "htan_ohsu": 3410328,
    "act": 464532,
    "adamjtaylor": 3421936,
    "lambda": 3413795,
    "all_registered_synapse_users": 273948,
    "anyone_on_the_web": 273949,
}

# Define permission levels
# fmt: off
permission_levels = {
    "view":     ["READ"],
    "download": ["READ", "DOWNLOAD"],
    "edit":     ["READ", "DOWNLOAD", "CREATE", "UPDATE"],
    "delete":   ["READ", "DOWNLOAD", "CREATE", "UPDATE", "DELETE"],
    "admin":    ["READ", "DOWNLOAD", "CREATE", "UPDATE", "DELETE", "MODERATE", "CHANGE_PERMISSIONS", "CHANGE_SETTINGS"],
}
# fmt: on


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


public_view_resource_access = {
    "principalId": principals["anyone_on_the_web"],
    "accessType": permission_levels["view"],
}
registered_user_download_resource_access = {
    "principalId": principals["all_registered_synapse_users"],
    "accessType": permission_levels["download"],
}

for e in tqdm(entity_ids):
    # Fetch the current ACL for the entity
    current_acl = get_acl(e)

    # Make a custom acl
    custom_acl = current_acl

    # Add public view and registered user download permissions to the ACL
    custom_acl.append(public_view_resource_access)
    custom_acl.append(registered_user_download_resource_access)

    put_acl(e, custom_acl)
