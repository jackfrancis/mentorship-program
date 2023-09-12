import logging
import sys
import os
import openai
import json
import pandas as pd

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
    mentors_df = pd.DataFrame()
    mentees_df = pd.DataFrame()
    return mentors_df, mentees_df #TODO: Remove once implemented

    # Read in mentor and mentee CSV files
    mentors_df = pd.read_csv("mentors.csv")
    mentees_df = pd.read_csv("mentees.csv")

# Process the data so it can be sent to GPT, ideally into JSON structure.
def preprocess_data(mentors_df, mentees_df):
    return "" #TODO: Need to implement

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

    mentors_df, mentees_df = retrieve_data()
    logging.info("Data retrieved")

    inputdata = preprocess_data(mentors_df, mentees_df)

    logging.info(f"Preprocess_data: {inputdata}")

    # TODO: remove once we're using real data
    inputdata = "tell me a joke"

    response = match_with_gpt(inputdata)

    logging.info(f"Matching response: {response}")

    postprocess_data(response)

    logging.info("Finished")
