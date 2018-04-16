## A server to return signed S3 urls. 

### Getting Started:

* Update the file `s3_server.py` with the required details. 
* Install dependencies : (pip install) boto, falcon, falcon_cors, gunicorn 
* Run the server `gunicorn s3_server:api`

Or: Docker
* Edit `s3_server.py`
* Build and run the Dockerfile (`docker run -p 8000:8000 <image id>`)

Or: Deployment using vault and docker

* To deploy using docker and [vault](https://www.vaultproject.io/), build the image from the Dockerfile, or pull it from the docker hub: `tb15/s3_server:master` 

* The image will read the vault credentials from an environment variable, then use sed to edit the s3_server.py file to update the database credentials. You will need to pass the vault client token, server url and index within vault to the image.

e.g: 

```
docker run -d -p 8000:8000 -it \
  -e TOKEN=${TOKEN} \
  -e URL=${VAULT_ADDR} \
  -e INDEX=tag-validator/s3 \
  tb15/s3_server:master
  ```
The server will serve at `http://localhost:8000/api/S3Sign` 

Example Query using httpie :
    
```json
 $ http GET 'http://127.0.0.1:8000/api/S3Sign?objectName=log.txt'HTTP/1.1 200 OK
Connection: close
Date: Fri, 09 Feb 2018 15:29:30 GMT
Server: gunicorn/19.7.1
content-length: 162
content-type: application/json; charset=UTF-8

{
    "signedUrl": "https://cog.sanger.ac.uk:443/tb15/uploads/log.txt?Signature=Sc1fSryIPlslX092eKVrZmXVjSU%3D&Expires=1518190470&AWSAccessKeyId=QNTED0B3JWYME5G1S56A"
}
```

Test using Curl: (the server will print the guessed file type to pass as a header)

```bash
$ curl -H "Content-Type: text/plain" -T "log.txt" https://cog.sanger.ac.uk:443/tb15/uploads/log.txt\?Signature\=WTqc9VfhzDdwsho1nBkl4jxI1tg%3D\&Expires\=1518189029\&AWSAccessKeyId\=QNTED0B3JWYME5G1S56A
```

Example Use: 

```javascript
fetch("/api/S3Sign?objectName=" + fileName, {
      method: "GET"
    })
      .then(
        url => url.json(),
        error => console.log("Error generating signed URL", error)
      )
      .then(url =>
        fetch(url.signedUrl, {
          method: "PUT",
          body: file
        })
      )
 ```
I used nginx to reverse proxy connections to the gunicorn server. (Avoids needless CORS Issues)

This config worked for me : 

```
location /api {

        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        rewrite ^/api/?(.*) /$1 break;
        proxy_pass http://127.0.0.1:8000;
        proxy_redirect off;
}
```
