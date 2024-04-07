# 🔥 Scripts to reset ACLs within HTAN's Synapse projects

`reset_dev.py`: 
This script automates the verification and adjustment of ACL inheritance for entities within a Synapse project, ensuring all adhere to project-level permissions.

`set_project_acl.py`: 
This script modifies Access Control Lists (ACLs) for a Synapse project, setting custom permissions for specified users or teams based on predefined permission levels.

`make_L3_L4_public.py`: This script updates Access Control Lists (ACLs) for entities in a Synapse project, based on entity IDs retrieved from a Google BigQuery query of HTAN's released L3 and L4 files. It assigns view permissions to anyone on the web and download permissions to all registered Synapse users for each entity matching specific criteria in the BigQuery dataset.

Requirements: 
- Synapse account with admin privilidges into all entities required
- A Synapse fileview scoped to all files and folders within target projects
- Google Cloud account with access to the `htan-dcc` project
