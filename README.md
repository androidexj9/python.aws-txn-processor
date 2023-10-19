# Stori© Code Challenge Project - python.aws-txn-processor
AWS Lambda Project for Stori© Code Challenge

## Architecture
![alt text](https://github.com/androidexj9/python.aws-txn-processor/blob/main/static/stori-code-challenge.drawio.png)

## Python Setup
```
$ python3 -m venv .venv
```

```
source .venv/bin/activate
```

```
(.venv) python3 -m pip install -r requirements.txt
```

```
coverage run -m pytest
```


## Build and push Docker image to AWS

### Create docker image:
```
docker build -t txn-processor .
```

### Create AWS ECR repository:
```
aws ecr create-repository --repository-name txn-processor
```

### Tag docker image:
```
docker tag txn-processor:latest <repositoryUri>:latest
```
```
docker tag txn-processor:latest 018042299534.dkr.ecr.us-east-1.amazonaws.com/txn-processor:latest
```

### Retrieve an authentication token and authenticate your Docker client to your registry.
### Use the AWS CLI:
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 018042299534.dkr.ecr.us-east-1.amazonaws.com
```

### Push docker images to ECR:
```
docker push <repositoryUri>:latest
```
```
docker push 018042299534.dkr.ecr.us-east-1.amazonaws.com/txn-processor:latest
```

## Summary Account Balance email
![alt text](https://github.com/androidexj9/python.aws-txn-processor/blob/main/static/email-summary-account-balance.png)

## References
https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html
https://docs.aws.amazon.com/lambda/latest/dg/python-image.html