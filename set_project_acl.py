import synapseclient
import json

syn = synapseclient.Synapse()
syn.login()

# Your project ID and the FileView ID
project_id = 'syn55259805'
fileview_id = 'syn55259830'

# Users or teams
htan_dcc_admins = 3497313
htan_dcc = 3391844
htan_ohsu = 3410328
act = 464532

adamjtaylor = 3421936


# Permission levels
view          = ['READ']
download      = ['READ', 'DOWNLOAD']
edit          = ['READ', 'DOWNLOAD','CREATE', 'UPDATE']
delete        = ['READ', 'DOWNLOAD','CREATE', 'UPDATE', 'DELETE']
administrator = ['READ', 'DOWNLOAD','CREATE', 'UPDATE', 'DELETE', 'MODERATE', 'CHANGE_PERMISSIONS', 'CHANGE_SETTINGS']


def get_acl(entity_id):
    uri = f"/entity/{entity_id}/acl"
    acl = syn.restGET(uri)
    return(acl) 

def put_acl(entity_id, acl):
    uri = f"/entity/{entity_id}/acl"
    syn.restPUT(uri, json.dumps(acl)) 

acl = get_acl(project_id)
print(acl)

# Write custom_acl
new_acl = acl

new_acl['resourceAccess'] = [
        {
            'principalId': htan_dcc_admins, 
            'accessType': administrator
        },
        {
            'principalId': act, 
            'accessType': administrator
        },
        {
            'principalId': htan_dcc, 
            'accessType': edit
        },
        {
            'principalId': htan_ohsu, 
            'accessType': edit
        }
    ]

print(new_acl)

put_acl(project_id, new_acl)