###############################################################################
# Build stage
###############################################################################

# Use a specific Node.js version
FROM node:22-bookworm AS builder

# Set the working directory inside the container
WORKDIR /code

# Copy package.json and package-lock.json first for better layer caching
COPY package*.json ./

# Set environment variables for install / build
ARG NUXT_BACK_HOST_URL=${NUXT_BACK_HOST_URL}
ARG NUXT_BACK_WS_URL=${NUXT_BACK_WS_URL}
ENV NODE_ENV=production

# Install dependencies first to leverage Docker cache if dependencies don’t change
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

###############################################################################
# Runtime stage -currently, not very useful as we use the same runtime image
# (slim and alpine create a 404 with Dokploy)
###############################################################################

FROM node:22-bookworm AS runtime

WORKDIR /code

# Copy only the necessary files from the build stage
COPY --from=builder /code/.output ./.output
