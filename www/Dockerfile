FROM node:latest

COPY ./ ./
#Rebuild image only when package.json file change
RUN npm install

CMD ["npm", "start"]