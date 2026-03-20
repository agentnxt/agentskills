FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist/ ./dist/
ENV LOGTO_ENDPOINT=""
ENV LOGTO_APP_ID=""
ENV LOGTO_APP_SECRET=""
ENV LOGTO_ACCOUNTS_TOKEN=""
ENTRYPOINT ["node", "dist/index.js"]
