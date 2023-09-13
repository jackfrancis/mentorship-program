import logging
import sys
import os
import openai
import json
import pandas as pd
import requests

# Set up OpenAI API key
openai.api_key = os.environ.get('OPENAI_API_KEY')

# setup the logger to log to stdout and file
def setup_logger():
    logging.basicConfig(level=logging.DEBUG, filename='matching.log', format='%(asctime)s - %(levelname)s - %(message)s')

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    # only log INFO and above to stdout
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

# Retrieve mentor/mentee data
def retrieve_data():
    # Read in survey responses CSV files
    responses_df = pd.read_excel("responses.xlsx")

    return responses_df

# Process the data so it can be sent to GPT, ideally into JSON structure.
def preprocess_data(responses_df):
    # Set up authentication headers
    # see https://learn.microsoft.com/en-us/graph/auth/auth-concepts#access-tokens
    access_token = os.environ.get('ACCESS_TOKEN')
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    for index, participant in responses_df.iterrows():
        print(f"Processing participant {index} of {len(responses_df)}")
        alias = participant["Email"]

        # Use Microsoft Graph API to get manager
        response = requests.get(f"https://graph.microsoft.com/v1.0/users/{alias}/manager", headers=headers)
        manager = response.json().get('userPrincipalName')
        participant["manager"] = manager
    
        # Use Microsoft Graph API to get skip manager
        response = requests.get(f"https://graph.microsoft.com/v1.0/users/{manager}/manager", headers=headers)
        skip_manager = response.json().get('userPrincipalName')
        participant["skip_manager"] = skip_manager

        # Use Microsoft Graph API to get title
        response = requests.get(f"https://graph.microsoft.com/v1.0/users/{alias}", headers=headers)
        title = response.json().get('jobTitle')
        participant["title"] = title

    return responses_df

# Send message to OpenAI API and return the response
def match_with_gpt(inputdata):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=
            [{"role": "system", "content": 'You will match mentors with mentees based on their preferences ... or follow other instructions.'}, #TODO: Update system prompt
             {"role": "user", "content": f'{inputdata}'}],
    )
    completion = json.loads(str(response))

    return completion["choices"][0]["message"]["content"]

# TODO: Post process the results
def postprocess_data(matches):
    return #TODO: Remove once implemented

    # Write matches to CSV
    matches_df = pd.DataFrame(matches)
    matches_df.to_csv("matches.csv", index=False)


if __name__ == '__main__':

    setup_logger()
    logging.info("Initializing...")

    responses_df = retrieve_data()
    logging.info("Data retrieved")

    inputdata = preprocess_data(responses_df)

    logging.info(f"Preprocess_data: {inputdata}")

    # TODO: remove once we're using real data
    inputdata = "tell me a joke"

    response = match_with_gpt(inputdata)

    logging.info(f"Matching response: {response}")

    postprocess_data(response)

    logging.info("Finished")
