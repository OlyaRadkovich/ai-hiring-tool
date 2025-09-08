FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY src/. ./

EXPOSE 8080
CMD ["npm", "run", "dev", "--", "--host"]