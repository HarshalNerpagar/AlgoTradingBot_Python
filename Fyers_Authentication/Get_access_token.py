from fyers_apiv3 import fyersModel
file1 = open('AUTH_CODE.txt', 'r')
auth_code = file1.readlines()[0]

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



session.set_token(auth_code)
response = session.generate_token()

file1 = open("access_token", "w") #append mode
file1.write(list(response.items())[3][1])
file1.close()