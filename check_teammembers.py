import synapseclient
import pandas as pd

syn = synapseclient.Synapse()
syn.login()

print(syn.getUserProfile()["company"])

team_id = "3391844"  # HTAN_DCC
# team_id = "3410328"  # HTAN_OHSU
# team_id = "3438869"  # FAIR_Data

team = syn.getTeam(team_id)

print(f"Team {team_id}:")
print(pd.json_normalize(team))


team_memmbers = [*syn.getTeamMembers(team_id)]
team_memmbers_df = pd.json_normalize(team_memmbers)

team_memmbers_df["certified"] = team_memmbers_df["member.ownerId"].map(
    lambda x: syn.is_certified(x)
)


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


print(f"Test for user id 3421936: ORCID = {get_user_orcid('3421936')}")


team_memmbers_df["affiliation"] = team_memmbers_df["member.userName"].map(
    get_user_company
)
team_memmbers_df["orcid"] = team_memmbers_df["member.ownerId"].map(get_user_orcid)

print(f"Team members of {team_id}:")
print(team_memmbers_df.sort_values("isAdmin"))

# Check certification status
