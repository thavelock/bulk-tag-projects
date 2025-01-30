
import urllib.parse
import csv
import requests
import json
from argparse import ArgumentParser

SNYK_V1_API_BASE_URL      = 'https://api.snyk.io/v1'

SNYK_REST_API_BASE_URL      = 'https://api.snyk.io'
SNYK_REST_API_VERSION       = '2024-10-15'
SNYK_API_TIMEOUT_DEFAULT    = 90

RESPONSE_SUCCESS            = 200
RESPONSE_ERROR_RATE_LIMIT   = 429

RATE_LIMIT_BACKOFF_SEC      = 60

def main():

    parser = ArgumentParser()

    parser.add_argument("--snyk-token", dest="snyk_token", help="your Snyk Token", required=True)
    parser.add_argument("--csv-path", dest="csv_path", help="path to CSV file", required=True)
    parser.add_argument("--tag-key", dest="tag_key", help="Tag key", required=True)
    parser.add_argument("--tag-value", dest="tag_value", help="Tag Value", required=True)

    args = parser.parse_args()
    
    snyk_token = args.snyk_token
    csv_path = args.csv_path
    tag_key = args.tag_key
    tag_value = args.tag_value

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)

        for row in csv_reader:
            # ORG_NAME, PROJECT_NAME

            org_name = row[0]
            project_name = row[1]

            org_id = get_org_id(snyk_token, org_name)
            project_id = get_project_id(snyk_token, org_id, project_name)

            tag_project(snyk_token, org_id, project_id, tag_key, tag_value)


def get_project_id(snyk_token, org_id, project_name):
    headers = {
        'Authorization': f'token {snyk_token}',
    }

    base_url = SNYK_REST_API_BASE_URL

    url = f'{base_url}/rest/orgs/{org_id}/projects?version={SNYK_REST_API_VERSION}&limit=10&names={urllib.parse.quote_plus(project_name)}'

    response = requests.request(
        'GET',
        headers=headers,
        url=url
    )

    if response.status_code == RESPONSE_SUCCESS:
        # ---------- SUCCESS BLOCK ----------
        return json.loads(response.content)['data'][0]['id']
    else:
        # ---------- FAILURE BLOCK ----------
        print(f'ERROR: Could not retrieve project {project_name}, reason: {response.status_code}')
        
    return

def get_org_id(snyk_token, org_name):
    headers = {
        'Authorization': f'token {snyk_token}',
    }

    base_url = SNYK_REST_API_BASE_URL

    url = f'{base_url}/rest/orgs?version={SNYK_REST_API_VERSION}&limit=10&slug={urllib.parse.quote_plus(org_name)}'

    response = requests.request(
        'GET',
        headers=headers,
        url=url
    )

    if response.status_code == RESPONSE_SUCCESS:
        # ---------- SUCCESS BLOCK ----------
        return json.loads(response.content)['data'][0]['id']
        pass
    else:
        # ---------- FAILURE BLOCK ----------
        print(f'ERROR: Could not retrieve org {org_name}, reason: {response.status_code}')
        
    return None

def tag_project(snyk_token, org_id, project_id, tag_key, tag_value):
    headers = {
        'Authorization': f'token {snyk_token}',
    }

    base_url = SNYK_V1_API_BASE_URL

    url = f'{base_url}/org/{org_id}/project/{project_id}/tags'

    tag = {
        "key": f"{tag_key}",
        "value": f"{tag_value}"
    }

    response = requests.request(
        'POST',
        headers=headers,
        url=url,
        json=tag
    )

    if response.status_code == RESPONSE_SUCCESS:
        # ---------- SUCCESS BLOCK ----------
        print(f"Successfully tagged {project_id} with {tag_key}:{tag_value}")
    else:
        # ---------- FAILURE BLOCK ----------
        if response.status_code == 422:
            print(f'{tag_value} already exists for project: {project_id}')
        else:
            print(f'ERROR: Could not apply tag: {tag_value} to project: {project_id}, reason: {response.status_code}')

if __name__ == '__main__':
    main()