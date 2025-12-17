FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy shared module first
COPY shared/ ./shared/
WORKDIR /app/shared
RUN go mod download

# Copy user-service code
WORKDIR /app
COPY user-service/ ./user-service/
WORKDIR /app/user-service
RUN go mod download
RUN go build -o user-service .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/user-service/user-service .
EXPOSE 8084
CMD ["./user-service"]


