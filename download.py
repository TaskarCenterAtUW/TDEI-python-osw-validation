import os
import requests

FILES_TO_UPLOAD = [
    'graph-10.xml',
    'graph-30.xml',
    'graph-50.xml',
    'graph-70.xml',
    'graph-90.xml',
    'graph-100.xml',
    'graph-200.xml',
    'graph-250.xml',
    'kingCounty-130.xml',
    'seattle.new.xml',
    'tacoma.xml',
    'vancouver.xml',
]


def download_file(url: str, download_folder: str = 'downloads'):
    # Create the download folder if it doesn't exist
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    # Download the file
    print(f"Downloading file from {url}...")
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        # Try to get the file name from the Content-Disposition header
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"')
        else:
            # Fall back to using the last part of the URL as the file name
            filename = url.split('/')[-1]

        file_path = os.path.join(download_folder, filename)

        # Write the file
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)

        print(f"File downloaded successfully and saved to {file_path}")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")

# Example usage

for i in FILES_TO_UPLOAD:
    url = f'https://tdeisamplestorage.blob.core.windows.net/tdei-storage-test/input/{i}'
    download_file(url, '/Users/anuj/Work/Gaussian/TDEI-python-osw-validation/xml')
