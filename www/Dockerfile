FROM node:latest
WORKDIR '/www/src'

#Rebuild image only when package.json file change
COPY package.json ./
RUN npm install
COPY . .

RUN node app.js