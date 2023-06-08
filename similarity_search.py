import requests
import json

def search_documents(search_query, k):
    # Set the endpoint and API key for your Azure Cognitive Search service
    search_endpoint = "https://asap-km-prod-s.search.windows.net"
    api_key = "pP2N8rf2U7F7DGHwwQGdo73oKT0l3jFrq7wyDq2KqjAzSeAU1ga2"
    document_id = '231'

    # Set the name of your search index
    index_name = "documents-v2"

    # Build the request URL
    # url = f"{search_endpoint}/indexes/{index_name}/docs/search?api-version=2020-06-30"
    url = f"{search_endpoint}/indexes/{index_name}/docs/search?api-version=2020-06-30"

    # Set the request headers
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # Create the request body
    request_body = {
        "search": search_query,
        "queryType": "full",
        "top": k
    }

    # Send the search request
    response = requests.post(url, headers=headers, json=request_body)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        search_results = response.json()
        # Extract and return the search results
        return search_results["value"]
    else:
        print(f"Search request failed with status code: {response.status_code}")
        return None
