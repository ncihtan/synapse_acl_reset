import synapseclient
import json
import yaml

# Initialize the Synapse client and log in
syn = synapseclient.Synapse()
syn.login()

# Load configuration from the external YAML file
config_file_path = "config.yaml"
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

# Assign values from the YAML config
# fileview_id = config["fileview_id"]
principals = config["principals"]
permission_levels = config["permission_levels"]

# Project and FileView IDs
# test
project_id = "syn55259805"
fileview_id = "syn55259830"


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


# Fetch the current ACL for the project
current_acl = get_acl(project_id)

# Define specific resource access for the ACL
custom_acl = current_acl

# fmt: off
custom_acl["resourceAccess"] = [
    {"principalId": principals["dcc_admin"], "accessType": permission_levels["admin"]},
    {"principalId": principals["act"],       "accessType": permission_levels["admin"]},
    {"principalId": principals["lambda"],    "accessType": permission_levels["delete"]},
    {"principalId": principals["dcc"],       "accessType": permission_levels["edit"]},
    {"principalId": principals["ohsu"],      "accessType": permission_levels["edit"]},
    {"principalId": principals["nci"],       "accessType": permission_levels["view"]},
]
# fmt: on

# Apply the new ACL to the project
put_acl(project_id, custom_acl)
