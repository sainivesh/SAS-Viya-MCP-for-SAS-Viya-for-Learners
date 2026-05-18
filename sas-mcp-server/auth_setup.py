import os
import requests
import dotenv
from pathlib import Path

def main():
    # Find .env file in the same directory
    env_path = Path(__file__).parent / ".env"
    
    # Load existing env vars to find the endpoint
    dotenv.load_dotenv(env_path)
    endpoint = os.getenv("VIYA_ENDPOINT", "https://vfl-028.engage.sas.com")
    
    print("===================================================================")
    print("      SAS VIYA AUTHENTICATION SETUP (ONE-TIME SETUP)               ")
    print("===================================================================")
    print("This script will generate a permanent Refresh Token so you never")
    print("have to manually update your access tokens again!")
    print("\n1. Please click the following link and log in via your browser:")
    print("")
    
    auth_url = f"{endpoint}/SASLogon/oauth/authorize?client_id=sas.cli&response_type=code"
    print(f"   {auth_url}")
    print("")
    print("2. Look at the URL in your browser's address bar. It will look like this:")
    print("   http://localhost/SASLogon/oauth/authorize?code=XXXXXXXXX")
    print("")
    
    code = input("3. Please copy just the 'code' value and paste it here: ").strip()
    
    if not code:
        print("No code provided. Exiting.")
        return
        
    print(f"\nAttempting to trade code for a permanent Refresh Token...")
    
    token_url = f"{endpoint}/SASLogon/oauth/token"
    auth = ("sas.cli", "")
    data = {
        "grant_type": "authorization_code",
        "code": code
    }
    
    try:
        # Avoid insecure request warnings for cleaner output
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        response = requests.post(token_url, auth=auth, data=data, verify=False)
        response.raise_for_status()
        token_data = response.json()
        
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        
        if not refresh_token:
            print("ERROR: Authentication succeeded, but no refresh token was provided by SAS Viya.")
            return

        print("\nSUCCESS! Saving tokens to your .env file...")
        
        # Save securely to .env using python-dotenv
        dotenv.set_key(env_path, "VIYA_ACCESS_TOKEN", access_token)
        dotenv.set_key(env_path, "VIYA_REFRESH_TOKEN", refresh_token)
        
        print("-------------------------------------------------------------------")
        print("Setup complete! Your MCP server is now permanently authenticated.")
        print("You may now start your MCP server normally.")
        print("-------------------------------------------------------------------")
            
    except requests.exceptions.HTTPError as e:
        print(f"\nFailed to trade code for token: {e}")
        print("Response Content:")
        print(response.text)

if __name__ == "__main__":
    main()
