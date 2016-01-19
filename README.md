# insights-container

Note: you do not need to pull this repo to run. Simply use the dockerfile to build an image:

    docker build -t insights:rht . 

Note: You must add your Redhat username and password where appropraite in the dockerfile


Then run the image with the appropraite mounts: 

    docker run --privileged=true -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker/:/var/lib/docker/ -v /dev/:/dev/ insights:rht python /home/insights-docker/__init__.py  
