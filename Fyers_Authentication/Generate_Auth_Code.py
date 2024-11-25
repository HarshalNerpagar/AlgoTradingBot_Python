# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel


# Replace these values with your actual API credentials
client_id = "OVUPFX8VX5-100"
secret_key = "VST9T3O94Q"
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
response_type = "code"
state = "sample_state"
grant_type = "authorization_code"

# Create a session model with the provided credentials
session = fyersModel.SessionModel(
    client_id=client_id,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type,
    grant_type=grant_type
)

response = session.generate_authcode()
print(response)

# auth_code = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJpYXQiOjE3MjA3MDIxMjcsImV4cCI6MTcyMDczMjEyNywibmJmIjoxNzIwNzAxNTI3LCJhdWQiOiJbXCJ4OjBcIiwgXCJ4OjFcIiwgXCJkOjFcIiwgXCJkOjJcIiwgXCJ4OjBcIl0iLCJzdWIiOiJhdXRoX2NvZGUiLCJkaXNwbGF5X25hbWUiOiJYUjAwNjQyIiwib21zIjoiSzEiLCJoc21fa2V5IjoiNTczODRhZDQ1ZDIxMGVlMWIxZThkZTUzMTE4MjY3MWUzNjA0ZTM1N2M2ZDJkMzc5YmE1YjQ0YWQiLCJub25jZSI6IiIsImFwcF9pZCI6Ik9WVVBGWDhWWDUiLCJ1dWlkIjoiMGNiMjNhNTUzODgzNDA1MWE1NmZhZTU1ZmQyZWUxYzIiLCJpcEFkZHIiOiIwLjAuMC4wIiwic2NvcGUiOiIifQ.dZ57Q5dg2_iccvD6kFMloK5kxsUBFHwH7kfHC_Nkq40'

