FROM node:latest


COPY . ./www

WORKDIR /www

RUN apt-get update || : && apt-get install python3.6 -y
RUN apt-get install python3-pip -y
RUN pip3 install -r ./py/requirements.txt
RUN python -m spacy download en

RUN npm install

CMD ["npm", "start"]
