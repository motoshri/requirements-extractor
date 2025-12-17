FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy shared module first
COPY shared/ ./shared/
WORKDIR /app/shared
RUN go mod download

# Copy gateway code
WORKDIR /app
COPY gateway/ ./gateway/
WORKDIR /app/gateway
RUN go mod download
RUN go build -o gateway .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/gateway/gateway .
EXPOSE 8080
CMD ["./gateway"]


