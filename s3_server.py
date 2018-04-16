import boto
import boto.s3.connection
import falcon
from falcon_cors import CORS
import mimetypes

"""
S3 Signed URL API. Will Guess filetype passed.

Run with gunicorn: $ gunicorn s3_server:api

"""

access_key = 'ACC_KEY' #Fill in
secret_key = 'SEC_KEY' #Fill in
conn = boto.connect_s3(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    host='GATEWAY_URL',         # Fill in 
    # is_secure=False,               # uncomment if you are not using ssl
    calling_format=boto.s3.connection.OrdinaryCallingFormat(),
)

# Allow access via CORS requests.
cors = CORS(allow_origins_list=['http://localhost:3000'], 
            allow_headers_list=['Access-Control-Allow-Origin'])


class signS3Upload(object):
    def on_get(self, req, resp):
        """Handles get requests"""
        print("req data is: ", req.params)
        resp.status = falcon.HTTP_200
        resp.media = self.sign_s3_upload(req.params)

    def sign_s3_upload(self, request):
        object_name = request['objectName']
        # Guess the MIME type to give to s3
        content_type = mimetypes.guess_type(object_name)[0]
        print("Guessed content type: ", content_type)

        signed_url = conn.generate_url(
            300,
            "PUT",
            'mybucket', #Bucket name
            'uploads/' + object_name, #Bucket folder
            headers={'Content-Type': content_type}
        )

        return {'signedUrl': signed_url}


api = falcon.API(middleware=[cors.middleware])
api.add_route('/S3Sign', signS3Upload())
