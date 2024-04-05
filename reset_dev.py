import synapseclient

syn = synapseclient.Synapse()
syn.login()

# Your project ID and the FileView ID
project_id = 'syn55259805'
fileview_id = 'syn55259830'

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

def verify_acl_inheritance():
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
    query_str = f"SELECT id FROM {fileview_id} WHERE benefactorId<>'{project_id}'"
    query_results = syn.tableQuery(query_str)
    entities_df = query_results.asDataFrame()

    if not entities_df.empty:
        print(f"Warning: There are {len(entities_df)} entities that do not inherit permissions from the project.")
        print(entities_df['id'])
    else:
        print("Success: All entities inherit permissions from the project.")

# Query the FileView for unique benefactor IDs
query_str = f"SELECT DISTINCT(benefactorId) as benefactorId FROM {fileview_id} WHERE projectId='{project_id}' AND benefactorId <> '{project_id}'"
query_results = syn.tableQuery(query_str)

# Fetch the results into a DataFrame
benefactors_df = query_results.asDataFrame()

print(benefactors_df)

for b in benefactors_df['benefactorId']:
    delete_acl(b)

verify_acl_inheritance()


