import requests

def authenticate_with_token(token):
    # Set the token in the header for authentication
    headers = {"Authorization": f"token {token}"}

    # GitHub API endpoint for user information
    user_url = 'https://api.github.com/user'

    # Send a GET request to the user endpoint with the token in the header
    response = requests.get(user_url, headers=headers)

    # Check if authentication was successful
    if response.status_code == 200:
        print("Authentication successful.")
        return True
    else:
        print("Authentication failed. Check your token.")
        return False

def get_repository_contents(owner, repo_name, token):
    # Set the token in the header for authentication
    headers = {"Authorization": f"token {token}"}

    # GitHub API endpoint for repository contents
    repo_contents_url = f'https://api.github.com/repos/{owner}/{repo_name}/contents'

    # Send a GET request to retrieve repository contents
    response = requests.get(repo_contents_url, headers=headers)

    # Check if request was successful
    if response.status_code == 200:
        # Parse the response JSON to extract file names
        contents = response.json()
        file_names = [content['name'] for content in contents if content['type'] == 'file']
        print("Repository contents:", file_names)
        return file_names
    else:
        print("Failed to retrieve repository contents. Check repository name and owner.")
        return None

def main():
    # Prompt the user to enter their personal access token
    github_token = input("Enter your GitHub personal access token: ")

    # Prompt the user to enter the repository owner's username and repository name
    repository_owner = input("Enter the GitHub repository owner's username: ")
    repository_name = input("Enter the GitHub repository name: ")

    # Authenticate with GitHub using personal access token
    if authenticate_with_token(github_token):
        # Retrieve repository contents
        get_repository_contents(repository_owner, repository_name, github_token)

if __name__ == "__main__":
    main()
