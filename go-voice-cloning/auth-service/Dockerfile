FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy shared module first
COPY shared/ ./shared/
WORKDIR /app/shared
RUN go mod download

# Copy auth-service code
WORKDIR /app
COPY auth-service/ ./auth-service/
WORKDIR /app/auth-service
RUN go mod download
RUN go build -o auth-service .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/auth-service/auth-service .
EXPOSE 8081
CMD ["./auth-service"]


