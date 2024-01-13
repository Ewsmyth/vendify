# vendify
 E-commerce Flask website

## Update Ubuntu Server
```
sudo apt update && sudo apt upgrade -y
```

## Install Docker on Ubuntu Server

##### Add Docker's official GPG key:
```
sudo apt-get install ca-certificates curl gnupg
```
```
sudo install -m 0755 -d /etc/apt/keyrings
```
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```
```
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```
##### Add the repository to Apt sources:
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
```
sudo apt-get update
```
##### Install Docker packages:
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

## Install Portainer with Docker
##### Create a volume that Portainer Server will use to store its database:
```
sudo docker volume create portainer_data
```
##### Download and install Portainer Server:
```
sudo docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```
##### Login to the admin account:
```
https://<serverip>:9443
```

## To download and install this application on Docker on Ubuntu Server run the following commands:

##### You can run this command in any directory you want I just run it from the home directory
```
sudo git clone https://github.com/Ewsmyth/vendify.git
```
##### This should be altered to the proper path to the directory you cloned the git into
```
cd vendify
```
##### The period is for if you are inside the "vendify" directory if you are not then you should replace this with the path to the Interactify directory
```
sudo docker build -t vendify-image .
```
##### Setup the database volume for persistent storage
```
sudo docker volume create vendify-data
```
##### Setup the userposts volume for persistent storage
```
sudo docker volume create vendify-uploads
```
##### Install Vendify
```
sudo docker run -d -p 8686:8686 --restart=unless-stopped \
    -v vendify-data:/var/lib/docker/volumes/vendify-data \
    -v vendify-uploads:/var/lib/docker/volumes/vendify-uploads \
    vendify-image
```

## To update Vendify:
#### Open Portainer and stop your Vendify server, then remove it, you can also remove the image since we will be creating a new image
##### Type ls and make sure you see the "vendify" directory, if you don't navigate to where your vendify directory is. Do not open the directory.
```
ls
```
##### Remove the directory:
```
sudo rm -r vendify
```
##### Import the website code using Git:
```
sudo git clone https://github.com/Ewsmyth/vendify.git
```
##### Open the new vendify directory:
```
cd vendify
```
##### Build the docker image:
```
sudo docker build -t vendify-image .
```
##### Since you should already have volumes for your data storage you dont need to make volume again.
##### Install Vendify and mount it to your pre-existing volumes
```
sudo docker run -d -p 8686:8686 --restart=unless-stopped \
    -v vendify-data:/var/lib/docker/volumes/vendify-data \
    -v vendify-uploads:/var/lib/docker/volumes/vendify-uploads \
    vendify-image
```