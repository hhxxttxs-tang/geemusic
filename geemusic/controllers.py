from flask import Response, stream_with_context, redirect,request
import requests
import boto3
from uuid import uuid4
from botocore.client import Config
from os import environ
from geemusic import app, api

BUCKET_NAME = environ.get("S3_BUCKET_NAME")


def proxy_response(req):
    s3 = boto3.resource('s3')
    s3_client = boto3.client('s3', config=Config(signature_version='s3v4'))

    bucket = s3.Bucket(BUCKET_NAME)
    file_name = str(uuid4())

    obj = bucket.put_object(
        Key=file_name,
        Body=req.content,
        ACL="authenticated-read",
        ContentType=req.headers["content-type"]
    )

    url = s3_client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": file_name},
        ExpiresIn=120
    )
    return redirect(url, 303)


@app.route('/wake-up')
def index():
    return 'I am not sleeping!'


@app.route("/alexa/stream/<song_id>")
def redirect_to_stream(song_id):
    app.logger.info('@app.route(/alexa/stream/%s), method = %s' % (song_id,request.method))
    google_stream_url = api.get_google_stream_url(song_id)
    app.logger.debug('Got google stream URL = %s' % google_stream_url)

    # Scrobble if Last.fm is setup
    if environ.get('LAST_FM_ACTIVE'):
        from .utils import last_fm
        song_info = api.get_song_data(song_id)
        last_fm.scrobble(
            song_info['title'],
            song_info['artist'],
            environ['LAST_FM_SESSION_KEY']
        )

    app.logger.debug("%s requst to google stream URL......" % request.method)
    if request.method == 'HEAD':
        req = requests.head(google_stream_url)
    elif request.method == 'GET':
        req = requests.get(google_stream_url, stream=False)
    else:
        app.logger.error('unexpected request method = ' % request.method)

    if environ.get('USE_S3_BUCKET') == "True":
        return proxy_response(req)

    app.logger.debug("send result of (%s request to google stream URL) to Alexa" % request.method)
    return Response(stream_with_context(req.iter_content(chunk_size=1024 * 1024)), content_type=req.headers['content-type'])
