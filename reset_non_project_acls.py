import synapseclient
import json
import tqdm
import argparse
import yaml

parser = argparse.ArgumentParser()
parser.add_argument(
    "htan_center", help="Name of key in config under projects and teams"
)
args = parser.parse_args()

syn = synapseclient.Synapse()
syn.login()

# Load configuration from the external YAML file
print("Loading configuration from YAML file")
config_file_path = "config.yaml"
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)

# Assign values from the YAML config

if args.htan_center == "test":
    fileview_id = "syn55259830"
else:
    fileview_id = config["fileview_id"]

# Project and team IDs for the HTAN Center
center_project_id = config["projects"][args.htan_center]


def verify_acl_inheritance(syn, project_id, fileview_id):
    """
    Verifies that all entities within a specified project inherit their ACLs directly
    from the project.

    This function queries a FileView to find entities whose benefactorId does not match
    the project ID, indicating they do not inherit their ACLs directly from the project.
    It prints a warning with the IDs of such entities if any are found. If no entities
    are found that deviate from the project's ACL, it confirms successful inheritance.

    Global Variables Used:
    - syn (synapseclient.Synapse): A logged-in Synapse client instance.
    - fileview_id (str): The Synapse ID of the FileView used for the query.
    - project_id (str): The Synapse ID of the project against which entities'
    ACL inheritance is verified.

    Exceptions:
    - May raise exceptions related to querying the FileView or processing the query
    results, propagated from the `synapseclient` methods used.

    Side Effects:
    - Makes a call to the Synapse REST API to perform a query on a FileView.
    - Prints to the console the outcome of the verification.
    """

    query_str = f"""
    SELECT DISTINCT(benefactorId) as id FROM {fileview_id} 
    WHERE benefactorId<>'{project_id}' AND projectId='{project_id}'
    """

    print(
        f"Querying {fileview_id} for benefactorIds not equal to projectId {project_id} ({args.htan_center})..."
    )
    query_results = syn.tableQuery(query_str)
    entities_df = query_results.asDataFrame()

    if not entities_df.empty:
        print(
            f"""
ACTION REQUIRED: There are {len(entities_df)} entities that do not inherit permissions from the project ({project_id})...
        """
        )
        return entities_df
    else:
        print(
            f"""
NO ACTION REQUIRED: All entities inherit permissions from the project ({project_id})
        """
        )
        exit()


def delete_acl(entity_id):
    """
    Deletes the Access Control List (ACL) for a given Synapse entity, making it inherit
    ACLs from its parent.

    This function attempts to delete the custom ACL for an entity specified by its ID.
    If the entity does not have a custom ACL (indicating it already inherits from its
    parent), the function will note that no deletion was necessary. If the Synapse API
    responds with an error other than a 404 (Not Found), the function will raise that
    error.

    Parameters:
    - entity_id (str): The Synapse ID of the entity whose ACL is to be deleted.

    Exceptions:
    - synapseclient.SynapseHTTPError: Raised for any Synapse API errors encountered
    during the ACL deletion process, other than 404 errors, which are handled within
    the function.

    Side Effects:
    - Makes a call to the Synapse REST API to delete an ACL, which may modify the
    permissions of the entity.
    - Prints to the console the outcome of the deletion attempt.
    """
    uri = f"/entity/{entity_id}/acl"
    try:
        syn.restDELETE(uri)
        print(f"Deleted ACL for entity: {entity_id}")
    except synapseclient.SynapseHTTPError as e:
        if e.response.status_code == 404:
            print(f"No custom ACL to delete for entity: {entity_id}")
        else:
            raise


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


def reset_acls(syn, project_id, fileview_id):

    # List current ACLs below the project level
    benefactors_df = verify_acl_inheritance(syn, project_id, fileview_id)

    print(
        f"""
ACLs for the following entities will be be removed and now inherited from {project_id}:
        """
    )
    print(benefactors_df["id"].to_list())

    # Confirm is user wants to continue
    response = input("Press 'y' to continue or 'n' to exit: ").lower()
    if response == "n" or response != "y":
        print(
            "Exiting script." if response == "n" else "Invalid input. Exiting script."
        )
        exit()

    # Initialise a empty list to store ACLs
    acls = []

    # For each benefactorId
    for b in tqdm.tqdm(benefactors_df["id"]):
        # Fetch the ACL
        acl = get_acl(b)
        # Append to acl list
        acls.append(acl)
        # Remove the ACL
        delete_acl(b)

    # Save the list of deleted ACLs to a json file
    print(f"Saving deleted ACLs to deleted_acls_{project_id}.json")
    with open(f"deleted_acls_{project_id}.json", "w", encoding="utf-8") as f:
        json.dump(acls, f, indent=2)


def main():
    # Reset the ACLs
    reset_acls(syn, center_project_id, fileview_id)

    # Confirm that all ACLs have been deleted
    verify_acl_inheritance(syn, center_project_id, fileview_id)


if __name__ == "__main__":
    main()
