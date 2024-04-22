import synapseclient
import json
import yaml
import sys
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument(
    "htan_center", help="Name of key in config under projects and teams"
)
args = parser.parse_args()

# Initialize the Synapse client and log in
syn = synapseclient.Synapse()
syn.login()


def get_acl(entity_id):
    """
    Uses the Synapse REST API to get the ACL of a specified entity

    Parameters:
    - entity_id (str): The Synapse ID of the entity whose ACL is to be fetched.
    """
    try:
        uri = f"/entity/{entity_id}/acl"
        acl = syn.restGET(uri)
        return acl
    except synapseclient.SynapseHTTPError as e:
        print(f"Error fetching ACL for entity: {entity_id}")
        raise


def put_acl(entity_id, acl):
    """
    Update the ACL for a given entity by its ID with a new ACL.

    Parameters:
    - entity_id (str): Synapse ID of the entity.
    - acl (dict): New ACL to apply to the entity.
    """
    try:
        uri = f"/entity/{entity_id}/acl"
        syn.restPUT(uri, json.dumps(acl))
    except synapseclient.SynapseHTTPError as e:
        print(f"Failed to update ACL for entity {entity_id}: {str(e)}")


def main():

    # Load configuration from the external YAML file
    print("Loading configuration from YAML file")
    config_file_path = "config.yaml"
    with open(config_file_path, "r") as file:
        config = yaml.safe_load(file)

    # Assign values from the YAML config
    fileview_id = config["fileview_id"]
    teams = config["teams"]
    users = config["users"]
    permission_levels = config["permission_levels"]

    # Project and team IDs for the HTAN Center
    center_project_id = config["projects"][args.htan_center]
    center_team_id = config["teams"][args.htan_center]

    print(f"    Project name: {args.htan_center}")
    print(f"    Project ID:   {center_project_id}")
    print(f"    Team ID:      {center_team_id}\n")

    # Fetch the current ACL for the project
    print("Fetching the current ACL for the project")
    current_acl = get_acl(center_project_id)

    # Define specific resource access for the ACL
    print("Defining specific resource access for the ACL")
    custom_acl = current_acl
    # fmt: off
    custom_acl["resourceAccess"] = [
        {"principalId": teams["dcc_admin"], "accessType": permission_levels["admin"]},
        {"principalId": teams["act"],       "accessType": permission_levels["admin"]},
        {"principalId": users["lambda"],    "accessType": permission_levels["delete"]},
        {"principalId": teams["dcc"],       "accessType": permission_levels["edit"]},
        {"principalId": center_team_id,      "accessType": permission_levels["edit"]},
    ]
    # fmt: on
    # Apply the new ACL to the project
    print("Applying the new ACL to the project")
    put_acl(center_project_id, custom_acl)
    print("Done!")


if __name__ == "__main__":
    main()
