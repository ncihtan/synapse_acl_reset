import synapseclient
import json

# Initialize the Synapse client and log in
syn = synapseclient.Synapse()
syn.login()

# Project and FileView IDs
# test
project_id = "syn55259805"
fileview_id = "syn55259830"

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


# Fetch the current ACL for the project
current_acl = get_acl(project_id)

# Define specific resource access for the ACL
custom_acl = current_acl

# fmt: off
custom_acl["resourceAccess"] = [
    {"principalId": principals["htan_dcc_admins"], "accessType": permission_levels["admin"]},
    {"principalId": principals["act"],             "accessType": permission_levels["admin"]},
    {"principalId": principals["lambda"],          "accessType": permission_levels["delete"]},
    {"principalId": principals["htan_dcc"],        "accessType": permission_levels["edit"]},
    {"principalId": principals["htan_ohsu"],       "accessType": permission_levels["edit"]},
]
# fmt: on

# Apply the new ACL to the project
put_acl(project_id, custom_acl)
