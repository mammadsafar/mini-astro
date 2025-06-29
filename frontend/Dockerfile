# frontend/Dockerfile

# مرحله اول: نصب وابستگی‌ها
FROM node:18-alpine AS deps
WORKDIR /app

RUN npm config set registry https://registry.npmmirror.com
RUN npm config set fetch-retries 5 \
  && npm config set fetch-retry-mintimeout 20000 \
  && npm config set fetch-retry-maxtimeout 120000

COPY package.json package-lock.json ./
RUN npm ci

# مرحله دوم: build برنامه
FROM node:18-alpine AS builder
WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY . .
# 👈 برای زمان build
COPY .env.production .env

ENV NODE_ENV=production
RUN npm run build

# مرحله سوم: اجرای برنامه
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
