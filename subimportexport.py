import re
import os
import json
import pickle
from typing import Iterator
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
# PATH = "/C:/Users/treve/Documents/pythonthings/Scripts/"
temp = (['secrets/client_secrets0.json', 'secrets/client_secrets1.json',
         'secrets/client_secrets2.json'], [8080, 8008, 8800])
CLIENT_SECRETS = {key[1]: temp[1][key[0]] for key in enumerate(temp[0])}

# CLIENT_SECRET = CLIENT_SECRETS[0]

def print_response(response):
    print(response)


def authenticate_user_export(file, user_exists, secrets_key):
    credentials = None
    if user_exists:
        if os.path.exists(f'temp/{file}.pickle'):
            print('Loading Credentials From File...')
            with open(f'temp/{file}.pickle', 'rb') as token:
                credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                secrets_key,
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly'
                ]
            )

            flow.run_local_server(port=CLIENT_SECRETS[secrets_key], prompt='consent',
                                  authorization_prompt_message='We out here')
            credentials = flow.credentials
    with open(f'temp/{file}.pickle', 'wb') as f:
        print('Saving Credentials for Future Use...\n\n\n')
        pickle.dump(credentials, f)
    return credentials


def authenticate_user_import(file, user_exists, secrets_key):
    credentials = None
    if user_exists:
        if os.path.exists(f'temp/{file}.pickle'):
            print('Loading Credentials From File...')
            with open(f'temp/{file}.pickle', 'rb') as token:
                credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
               secrets_key,
                scopes=[
                    'https://www.googleapis.com/auth/youtube.force-ssl'
                ]
            )

            flow.run_local_server(port=CLIENT_SECRETS[secrets_key], prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials
    with open(f'temp/{file}.pickle', 'wb') as f:
        print('Saving Credentials for Future Use...\n\n\n')
        pickle.dump(credentials, f)
    return credentials


def dump_to_file(obj, filename):
    with open(filename, 'w', encoding = "utf-8") as f:
        json.dump(obj, f, indent=4)


def paginated_results(youtube_listable_resource, list_request, limit_requests=50) -> Iterator:
    remaining = -1 if limit_requests is None else limit_requests
    while list_request and remaining != 0:
        try:
            list_response = list_request.execute()
        except HttpError as e:
            return e
        yield list_response
        list_request = youtube_listable_resource.list_next(list_request, list_response)
        remaining -= 1


def build_resource(properties):
    resource = {}
    for p in properties:
        # Given a key like "snippet.title", split into
        # "snippet" and "title", where "snippet" will be
        # an object and "title" will be a property in that object.
        prop_array = p.split('.')
        ref = resource
        for pa in range(0, len(prop_array)):
            is_array = False
            key = prop_array[pa]

            # For properties that have array values, convert a name like
            # "snippet.tags[]" to snippet.tags, and set a flag to handle
            # the value as an array.
            if key[-2:] == '[]':
                key = key[0:len(key)-2:]
                is_array = True

            if pa == (len(prop_array) - 1):
                # Leave properties without values
                # out of inserted resource.
                if properties[p]:
                    if is_array:
                        ref[key] = properties[p].split(', ')
                    else:
                        ref[key] = properties[p]
            elif key not in ref:
                # For example, the property is "snippet.title",
                # but the resource does not yet have a "snippet"
                # object. Create the snippet object here.
                # Setting "ref = ref[key]" means that in the
                # next time through the "for pa in range ..." loop,
                # we will be setting a property in the
                # resource's "snippet" object.
                ref[key] = {}
                ref = ref[key]
            else:
                # For example, the property is "snippet.description",
                #  and the resource already has a "snippet" object.
                ref = ref[key]
    return resource


def remove_empty_kwargs(**kwargs):
    good_kwargs = {}
    if kwargs is not None:
        for key, value in kwargs.items():
            if value:
                good_kwargs[key] = value
    return good_kwargs


def subscriptions_insert(client, properties, **kwargs):
    resource = build_resource(properties)
    kwargs = remove_empty_kwargs(**kwargs)
    response = client.subscriptions().insert(
        body = resource,**kwargs).execute()
    return print_response(response)


def main():
    # CLIENT_SECRETS = glob.glob("client_secrets*")
    secrets_key = "secrets/client_secrets0.json"
    val = True
    files = True
    credentials = None
    loop = True
    page_no = 0
    out = False
    allout = False
    if not os.path.exists('/home/nightwng120/Documents/GithubRepos/subimportexport/temp'):
        os.mkdir('/home/nightwng120/Documents/GithubRepos/subimportexport/temp', 0o666)
    while loop:
        print("\n(press q to quit)\n")
        print("Import or export subs i/e ?")
        inputData = input()
        if inputData.lower() == "i":

            print("|----------------------------------|")
            print("| 1) Insert subs from list         |")
            print("| 2) Insert subs from curated list |")
            print("|----------------------------------|")
            inputData = input()
            if inputData == '1':
                print("What files do you want to insert into your account?\nEnter file name: ", end=' ')
                file = input()
                while files:
                    if allout:
                        allout = False
                        break

                    credentials = authenticate_user_import(file, False, secrets_key)
                    youtube = build('youtube', 'v3', credentials=credentials)
                    while os.path.exists(f'temp/{file}{page_no}.json'):
                        if out:
                            out = False
                            break
                        elif allout:
                            break

                        with open(f'temp/{file}{page_no}.json', 'r') as f:
                            data = json.load(f)
                        page_no += 1

                        for item in data['items']:
                            if out:
                                break
                            elif allout:
                                break

                            buffer = item["snippet"]["resourceId"]['channelId']
                            print(f'From main\n---------------------------------{item}\n---------------------------------\n')
                            try:
                                # resource = 
                                subscriptions_insert(
                                        youtube, {'snippet.resourceId.kind':
                                                  'youtube# channel',
                                                  'snippet.resourceId.channelId':
                                                  f'{buffer}'}, part='snippet')
                            except HttpError as e:
                                print('An HTTP error %d occurred:\n%s' %
                                      (e.resp.status, e.content))
                                if e.resp.status == 403:
                                    print(CLIENT_SECRETS)
                                    print(f"Current Client Secret: {secrets_key}")
                                    parsedInt = list(map(int, re.findall(r'\d+', secrets_key)))
                                    next_key = "secrets/client_secrets" + str(parsedInt[0] + 1) + ".json"
                                    if next_key not in CLIENT_SECRETS :
                                        # CLIENT_SECRET = CLIENT_SECRETS[CLIENT_SECRETS.index(CLIENT_SECRET)]
                                        print("Out of client secrets to use")
                                        allout = True
                                    else:
                                        secrets_key = next_key 
                                        page_no += 1
                                        out = True
                                        break

                            else:
                                print('A subscription to \'%s\' was added.' % item)

            elif inputData == '2':
                print("What files do you want to insert into your account?\nEnter file name: ", end=' ')
                file = input()
                print("What files do you want to compare against?\nEnter file name: ", end=' ')
                file2 = input()
                while files:
                    if allout:
                        allout = False
                        break
                    credentials = authenticate_user_import(file, False, secrets_key)
                    youtube = build('youtube', 'v3', credentials=credentials)
                    if os.path.exists(f'temp/channelIds_{file2}.txt'):
                        with open(f'temp/channelIds_{file2}.txt', 'r') as f:
                            data2 = f.readlines()
                    else:
                        data2 = []

                    while os.path.exists(f'temp/{file}{page_no}.json'):
                        if out:
                            out = False
                            break
                        elif allout:
                            break
                        with open(f'temp/{file}{page_no}.json', 'r') as f:
                            data = json.load(f)
                            print(f"Loaded json file #{page_no}")

                        page_no += 1
                        print(f"Length of data: {len(data)}")
                        for item in data['items']:
                            if out:
                                break
                            elif allout:
                                break

                            for cid in data2:
                                buffer = item["snippet"]["resourceId"]['channelId']
                                buffer = buffer.strip()
                                cid = cid.strip()
                                if cid == buffer:
                                    buffer = item["snippet"]["title"]
                                    print(f"Channel id: {cid}\nChannel: {buffer}")
                                    val = False
                            if val:
                                buffer = item["snippet"]["resourceId"]['channelId']
                                print(f'From main\n---------------------------------{item}\n---------------------------------\n')

                                try:
                                    print("", end="")
                                    subscriptions_insert(youtube, {'snippet.resourceId.kind': 'youtube# channel', 'snippet.resourceId.channelId': f'{buffer}'}, part='snippet')
                                except HttpError as e:
                                    print(CLIENT_SECRETS)
                                    print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
                                    if e.resp.status == 403:
                                        print(f"Current Client Secret: {secrets_key}")
                                        parsedInt = list(map(int, re.findall(r'\d+', secrets_key)))
                                        next_key = "secrets/client_secrets" + str(parsedInt[0] + 1) + ".json"
                                        if e.resp.status == 403:
                                            print(CLIENT_SECRETS)
                                            print(f"Current Client Secret: {secrets_key}")
                                            if next_key not in CLIENT_SECRETS :
                                                #CLIENT_SECRET = CLIENT_SECRETS[CLIENT_SECRETS.index(CLIENT_SECRET)]
                                                print("Out of client secrets to use")
                                                allout = True
                                            else:
                                                secrets_key = next_key 
                                                page_no += 1
                                                out = True
                                                break
                                else:
                                    print("", end="")
                                    print('A subscription to \'%s\' was added.' % item)
                            else:
                                val = True

        elif inputData.lower() == 'e':
            print("\nWhat would you like to do?\n")
            print("|----------------------------------|")
            print("| 1) Get subs from new account     |")
            print("| 2) Get subs from current account |")
            print("| 3) Quit                          |")
            print("|----------------------------------|")
            inputData = input()
            if int(inputData) == 1:
                print("Enter name for credentials file")
                file = input()
                print("Enter name for sub files")
                name = input()

                while files:
                    print(f'Current Secret File: {secrets_key}\nCurrent Port: {CLIENT_SECRETS[secrets_key]}')
                    try:
                        credentials = authenticate_user_export(file, False, secrets_key)
                        youtube = build('youtube', 'v3', credentials=credentials)
                        request = youtube.subscriptions().list(part='snippet', order="alphabetical", maxResults=50, mine=True)
                        response = request.execute()
                        response = paginated_results(youtube.subscriptions(), request)
                        print("\n\n---Request Sent---\n\n")
                        break
                    except HttpError as e:
                        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
                        print(f"Current Client Secret: {secrets_key}")
                        print(f'Http Error Code: {e.resp.status}')
                        parsedInt = list(map(int, re.findall(r'\d+', secrets_key)))
                        next_key = "secrets/client_secrets" + str(parsedInt[0] + 1) + ".json"
                        if e.resp.status == 403:
                            print(CLIENT_SECRETS)
                            print(f"Current Client Secret: {secrets_key}")
                            print(f"Next Client Secret: {next_key}")
                            if next_key not in CLIENT_SECRETS :
                                print("Out of client secrets to use")
                                return
                            else:
                                secrets_key = next_key 
                                page_no += 1
                                continue
                subs = []
                ids = []

                for pageNum, subscriptionitems_list_response in enumerate(response):
                    for item in subscriptionitems_list_response["items"]:
                         channel_id = item["snippet"]["resourceId"]['channelId']
                         channel_name = item["snippet"]['title']
                         channellink = f"https://youtube.com/channel/{channel_id}"
                         ids.append(channel_id)
                         subs.append(f"{channel_name}: {channellink}\n")
                    if pageNum < 10:
                        buffer = f"{str(pageNum)}"
                        dump_to_file(subscriptionitems_list_response, f'temp/{name}{buffer}.json')
                        continue

                    dump_to_file(subscriptionitems_list_response, f'temp/{name}{pageNum}.json')

                if os.path.exists(f'temp/channelIds_{name}.txt'):
                    open(f'temp/channelIds_{name}.txt', 'w').close()
                for item in ids:
                    with open(f'temp/channelIds_{name}.txt', 'a') as f:
                        f.write(f'{item}\n')

            elif int(inputData) == 2:
                print("Enter name of credentials file")
                file = input()
                print("Enter name for sub files")
                name = input()
                while files:
                    credentials = authenticate_user_export(file, True, secrets_key)
                    youtube = build('youtube', 'v3', credentials=credentials)
                    try:
                        request = youtube.subscriptions().list(part='snippet', order = "alphabetical", maxResults = 50, mine = True)
                        response = request.execute()
                        response = paginated_results(youtube.subscriptions(), request)
                        break
                    except HttpError as e:
                        print('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
                        print(f"Current Client Secret: {secrets_key}")
                        parsedInt = list(map(int, re.findall(r'\d+', secrets_key)))
                        next_key = "secrets/client_secrets" + str(parsedInt[0] + 1) + ".json"
                        if e.resp.status == 403:
                            print(CLIENT_SECRETS)
                            print(f"Current Client Secret: {secrets_key}")
                            if next_key not in CLIENT_SECRETS:
                                # CLIENT_SECRET = CLIENT_SECRETS[CLIENT_SECRETS.index(CLIENT_SECRET)]
                                print("Out of client secrets to use")
                                return
                            else:
                                secrets_key = next_key 
                                page_no += 1
                                continue
                subs = []
                ids = []
                for pageNum, subscriptionitems_list_response in enumerate(response):
                    for item in subscriptionitems_list_response["items"]:
                        channel_id = item["snippet"]["resourceId"]['channelId']
                        channel_name = item["snippet"]['title']
                        channellink = f"https://youtube.com/channel/{channel_id}"
                        ids.append(channel_id)
                        subs.append(f"{channel_name}: {channellink}\n")
                    if pageNum < 10:
                        buffer = f"{str(pageNum)}"
                        dump_to_file(subscriptionitems_list_response, f'temp/{name}{buffer}.json')
                        continue

                    dump_to_file(subscriptionitems_list_response, f'temp/{name}{pageNum}.json')
                if os.path.exists(f'temp/channelIds_{name}.txt'):
                    open(f'temp/channelIds_{name}.txt', 'w').close()
                for item in ids:
                    with open(f'temp/channelIds_{name}.txt', 'a') as f:
                        f.write(f'{item}\n')

            else:
                print("invalid input")
        elif inputData.lower() == 'q':
            print("quitting...")
            loop = False
        else:
            print("invalid input")


if __name__ == '__main__':
    main()
