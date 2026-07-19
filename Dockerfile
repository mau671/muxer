# Build stage
FROM golang:1.26-alpine AS builder

WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download

COPY . .
# Build the binary
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o muxer cmd/muxer/main.go

# Runtime stage
FROM alpine:latest

# Install mkvtoolnix so the Go binary doesn't need to auto-download it
RUN apk add --no-cache mkvtoolnix

WORKDIR /app
COPY --from=builder /src/muxer /usr/local/bin/muxer

ENTRYPOINT ["muxer"]
