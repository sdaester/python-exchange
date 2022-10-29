docker stop exchange-api
docker build . -t jcorderop/exchange
docker run --rm --name exchange-api -p 5000:5000 -d jcorderop/exchange