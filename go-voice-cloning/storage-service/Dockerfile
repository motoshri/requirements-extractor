FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy shared module first
COPY shared/ ./shared/
WORKDIR /app/shared
RUN go mod download

# Copy storage-service code
WORKDIR /app
COPY storage-service/ ./storage-service/
WORKDIR /app/storage-service
RUN go mod download
RUN go build -o storage-service .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/storage-service/storage-service .
EXPOSE 8083
CMD ["./storage-service"]


