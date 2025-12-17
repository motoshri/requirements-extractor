FROM golang:1.21-alpine AS builder

WORKDIR /app

# Copy shared module first
COPY shared/ ./shared/
WORKDIR /app/shared
RUN go mod download

# Copy voice-service code
WORKDIR /app
COPY voice-service/ ./voice-service/
WORKDIR /app/voice-service
RUN go mod download
RUN go build -o voice-service .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/voice-service/voice-service .
EXPOSE 8082
CMD ["./voice-service"]


