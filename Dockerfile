FROM node:20-alpine

WORKDIR /app

COPY node/package*.json ./node/
RUN cd node && npm install --omit=dev

COPY . .

EXPOSE 3000 8080

CMD ["node", "node/server.js"]

