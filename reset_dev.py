import synapseclient
import json
import tqdm

from datetime import datetime
print(datetime.now())

syn = synapseclient.Synapse()
syn.login()

# Your project ID and the FileView ID
## test
project_id = 'syn55259805'
fileview_id = 'syn55259830'



def verify_acl_inheritance(syn, project_id, fileview_id):
    """
    Verifies that all entities within a specified project inherit their ACLs directly from the project.

    This function queries a FileView to find entities whose benefactorId does not match the project ID, indicating they do not inherit their ACLs directly from the project. It prints a warning with the IDs of such entities if any are found. If no entities are found that deviate from the project's ACL, it confirms successful inheritance.

    Global Variables Used:
    - syn (synapseclient.Synapse): A logged-in Synapse client instance.
    - fileview_id (str): The Synapse ID of the FileView used for the query.
    - project_id (str): The Synapse ID of the project against which entities' ACL inheritance is verified.

    Exceptions:
    - May raise exceptions related to querying the FileView or processing the query results, propagated from the `synapseclient` methods used.

    Side Effects:
    - Makes a call to the Synapse REST API to perform a query on a FileView.
    - Prints to the console the outcome of the verification.
    """
    query_str = f"SELECT DISTINCT(benefactorId) as id FROM {fileview_id} WHERE benefactorId<>'{project_id}' AND projectId='{project_id}'"
    query_results = syn.tableQuery(query_str)
    entities_df = query_results.asDataFrame()

    if not entities_df.empty:
        print(f"Warning: There are {len(entities_df)} entities that do not inherit permissions from the project.")
        print(entities_df['id'])
        return(entities_df)
    else:
        print("Success: All entities inherit permissions from the project.")
        exit()

def delete_acl(entity_id):
    """
    Deletes the Access Control List (ACL) for a given Synapse entity, making it inherit ACLs from its parent.

    This function attempts to delete the custom ACL for an entity specified by its ID. If the entity does not have a custom ACL (indicating it already inherits from its parent), the function will note that no deletion was necessary. If the Synapse API responds with an error other than a 404 (Not Found), the function will raise that error.

    Parameters:
    - entity_id (str): The Synapse ID of the entity whose ACL is to be deleted.

    Exceptions:
    - synapseclient.SynapseHTTPError: Raised for any Synapse API errors encountered during the ACL deletion process, other than 404 errors, which are handled within the function.

    Side Effects:
    - Makes a call to the Synapse REST API to delete an ACL, which may modify the permissions of the entity.
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
    uri = f"/entity/{entity_id}/acl"
    acl = syn.restGET(uri)
    return(acl) 


benefactors_df = verify_acl_inheritance(syn, project_id, fileview_id)

response = input("Press 'y' to continue or 'n' to exit: ").lower()
if response == 'y':
    pass
elif response == 'n':
    print("Exiting script.")
    exit()
else:
    print("Invalid input. Exiting script.")
    exit()

acls = []

for b in tqdm.tqdm(benefactors_df['id']):
    acl = get_acl(b)
    acls.append(acl)
    delete_acl(b)

with open(f'deleted_acls_{project_id}.json', 'w', encoding='utf-8') as f:
    json.dump(acls, f, indent=2)

# Confirm that all ACLs have been deleted
verify_acl_inheritance(syn, project_id, fileview_id)


