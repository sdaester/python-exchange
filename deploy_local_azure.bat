# Stop local container
set IMAGE_NAME=exchange
set REGISTRY=basketregistry.azurecr.io

docker stop %IMAGE_NAME%

# Build image
docker build . -t %REGISTRY%/%IMAGE_NAME%

# Run image locally
docker run --rm --name %IMAGE_NAME% -p 5000:5000 -d %REGISTRY%/%IMAGE_NAME%

# push Image to Azure
docker tag %REGISTRY%/%IMAGE_NAME%:latest %REGISTRY%/%IMAGE_NAME%:latest
docker push %REGISTRY%/%IMAGE_NAME%:latest