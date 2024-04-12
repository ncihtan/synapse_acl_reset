import synapseclient
import pandas as pd
import yaml
from tqdm import tqdm

syn = synapseclient.Synapse()
syn.login()

# Load configuration from the external YAML file
config_file_path = "config.yaml"
with open(config_file_path, "r") as file:
    config = yaml.safe_load(file)


team_id = "3391844"  # HTAN_DCC
# team_id = "3410328"  # HTAN_OHSU
# team_id = "3438869"  # FAIR_Data
team_id = "3410872"  # HTAN_BU


def get_user_company(username):
    try:
        # Replace 'syn.getUserProfile' with the actual method to fetch user profiles
        user_profile = syn.getUserProfile(username)
        return user_profile.get(
            "company", None
        )  # Assuming 'company' is a key in the returned dict
    except Exception as e:
        # Handle exceptions if user profile is not found or other errors occur
        print(f"Error fetching company for username {username}: {e}")
        return None


def get_user_orcid(id):
    try:
        uri = f"/user/{id}/bundle?mask=2"
        orcid = syn.restGET(uri)
        return orcid["ORCID"]
    except:
        return None


def get_teammember_info(team_id):
    team = syn.getTeam(team_id)

    team_memmbers = [*syn.getTeamMembers(team_id)]
    team_memmbers_df = pd.json_normalize(team_memmbers)

    team_memmbers_df["certified"] = team_memmbers_df["member.ownerId"].map(
        lambda x: syn.is_certified(x)
    )

    team_memmbers_df["affiliation"] = team_memmbers_df["member.userName"].map(
        get_user_company
    )
    team_memmbers_df["orcid"] = team_memmbers_df["member.ownerId"].map(get_user_orcid)

    return team_memmbers_df


teams = config["teams"]

teammember_info = []
for team_name, team_id in tqdm(teams.items()):
    info = get_teammember_info(team_id)
    info.insert(1, "teamName", team_name)
    teammember_info.append(info)

teammember_info = pd.concat(teammember_info)
print(teammember_info)

teammember_info.to_csv("teammember_info.csv")
