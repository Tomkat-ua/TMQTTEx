
container=TMQTTEx
img=tomkat/tmqttex

docker build -t $img .


docker container stop $container
docker container rm $container

#ports - host:container
docker run -d  -p 8084:80 \
    --restart always \
    --name $container \
    -e TZ=Europe/Kiev \
       $img