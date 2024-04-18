# 🔥 HTAN x Synapse ACL reset

## Scripts to reset ACLs within HTAN's Synapse projects

These scripts are designed to be run in the order presented

### (1) Set ACLs at the project level

`set_project_acl.py` modifies Access Control Lists (ACLs) for a Synapse project entity, setting custom permissions for specified users or teams based on predefined permission levels.

```{bash}
python set_project_acl.py ohsu
```

TODO: #5 Allow for multiple `center_key` entries to be listed (eg `ohsu duke` or `all`)

### (2) Reset non-project ACLs

`reset_non_project_acls.py` automates the verification and adjustment of ACL inheritance for entities within a Synapse project, ensuring all adhere to project-level permissions.

```{bash}
python reset_non_project_acls.py ohsu
```

### (3) Re-set public access to released entities

`make_public.py` updates Access Control Lists (ACLs) for entities in a Synapse project, based on entity IDs retrieved from a Google BigQuery query of HTAN's released L3 and L4 files. It assigns view permissions to anyone on the web and download permissions to all registered Synapse users for each entity matching specific criteria in the BigQuery dataset.

```{bash}
python make_public.py
```

### (4) Check team membership

`check_teammembers.py` fetches team details and team members for specified teams, checks their certification status, retrieves each member's company and ORCID, and displays sorted team member information based on administrative status.

```{bash}
python check_teammembers.py
```

### Requirements

- Synapse account with admin access into all entities required
- A `~/.synapseConfig` file with valid authentication credentials
- A Synapse fileview scoped to all files and folders within target projects
- Google Cloud account with access to the `htan-dcc` project
- A config file, `config.yaml` containing details of projects, teams, users, permission levels, fileview and public directories 
- Appropriate Python environment with dependencies. We provide an `environment.yml` file for Conda.

### Conda environment setup

Open a terminal in the root directory of your project (the same directory where your environment.yml file is located).

Run the following command to create a new Conda environment based on the environment.yml file:

```{bash}
conda env create -f environment.yml
```

This command creates a new Conda environment named synapse-acl-reset (as specified in the environment.yml file) and installs the dependencies listed in the file.

To activate the new Conda environment, run the following command:

```{bash}
conda activate synapse-acl-reset
```

Now, you can run the scripts in this project within the `synapse-acl-reset` Conda environment, which has all the necessary dependencies.