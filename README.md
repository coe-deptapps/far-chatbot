# FAR Chatbot
[//]: # ([![Build Status]&#40;https://travis-ci.com/chyke007/credible.svg?branch=master&#41;]&#40;https://travis-ci.com/chyke007/credible&#41;)
![version](https://img.shields.io/badge/version-0.4.0-blue)
![Python Version](https://img.shields.io/badge/Python-v3.9.x-yellow)


## Setup on AWS
1. Created an EC2 instance (Ubuntu t2.micro)
2. Installed docker and docker compose
3. Created an SSH key pair. Added the public key to Chris's github account. Enabled access to the CAEN group. Then globally set the user and email for github in the EC2 instance.
`git config --global user.name "Chris Puzzuoli"` `git config --global user.email "cpuzzuol@umich.edu"`
4. Cloned the far-chatbot repository to the EC2 instance inside the `/home/ubuntu` directory. `git clone git@github.com:coe-deptapps/far-chatbot.git`
5. Created a `.env` file in the root directory of the project (ask Chris for values)
6. Created a `logs/` directory in the root of the project.
7. Ran `docker-compose build` to build the containers.
8. Ran `docker-compose up -d` to start the containers (detached mode).
9. Installed nginx on the EC2 instance.
- `sudo apt update` 
- `sudo apt install nginx`
10. Set up SSL using self-signed certificates (since Certbot can't be used unless a domain is purchased).
- `sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt`
- `sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048`
  - `sudo nano /etc/nginx/snippets/self-signed.conf`
      - Add the following lines:
  
            ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
            ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
  
- `sudo nano /etc/nginx/snippets/ssl-params.conf`
  - Add the following lines:
  
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_prefer_server_ciphers on;
        ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
        ssl_dhparam /etc/ssl/certs/dhparam.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:10m;
        add_header Strict-Transport-Security "max-age=63072000; includeSubdomains; preload";
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
  
- `sudo nano /etc/nginx/sites-available/default`
  - Add the following lines:
  
        server {
            listen 80;
            server_name _;

            location / {
            return 301 https://$host$request_uri;
            }
        }
        server {
            listen 443 ssl;
            server_name _;
            
            ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
            ssl_certificate_key /etc/ssl/private/nginx-selfsigned.key;
            include /etc/nginx/snippets/ssl-params.conf;
            
            location / {
                proxy_pass http://localhost:9001;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }
        }
  - `sudo nginx -t` to test the configuration
  - `sudo systemctl restart nginx` to restart nginx

11. Set outbound rules for the EC2 instance to allow traffic on `port 443`.
12. The chatbot should now be accessible at `https://<EC2_PUBLIC_IP>`
13. To ensure redis is running, you can install redis on the EC2 instance (`sudo apt-get install redis-tools`) and run `redis-cli ping` to check if it's running (response will be `PONG` if successful).