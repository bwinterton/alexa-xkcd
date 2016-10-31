import requests
import xmltodict
import boto3
import botocore
import re

def get_latest_info():
    r = requests.get("https://xkcd.com/rss.xml")
    rss = xmltodict.parse(r.text)
    post = dict()
    post["url"] = rss["rss"]["channel"]["item"][0]["link"]
    post["num"] = re.search(r"xkcd.com\/([0-9]+)",
                            rss["rss"]["channel"]["item"][0]["link"]).group(1)
    post["image_url"] = re.search(r"<img src=\"(.*)\" title=",
                                  rss["rss"]["channel"]["item"][0]["description"]).group(1)
    post["alt"] = re.search(r"alt=\"(.*)\"",
                                  rss["rss"]["channel"]["item"][0]["description"]).group(1)
    post["name"] = rss["rss"]["channel"]["item"][0]["title"]

    return post

def s3_file_exists(bucket, filename):
    try:
        obj = boto3.resource('s3').Object(bucket, filename).get()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "NoSuchKey":
            return False
        else:
            raise e
    else:
        return true


def push_to_s3(latest):
    filename = latest["num"] + ".png" 
    path = "/tmp/" + filename

    # If the file already exists, then don't re-upload
    if s3_file_exists("xkcd-lambda", filename):
        return

    r = requests.get(latest["image_url"], stream=True)
    with open(path , 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)

    bucket = boto3.resource('s3').Bucket("xkcd-lambda")
    extraArgs = {
        'Metadata' : {
            'Title' : latest["name"],
            'Alt' : latest["alt"],
            "URL" : latest["url"]
        }
    }
    bucket.upload_file(path, filename, extraArgs)

    return

def lambda_handler(event, context):
    main()

def main():
    latest = get_latest_info()
    push_to_s3(latest)


if __name__ == "__main__":
    main()
