module github.com/voice-cloning/user-service

go 1.21

replace github.com/voice-cloning/shared => ../shared

require (
	github.com/gorilla/mux v1.8.1
	github.com/jmoiron/sqlx v1.3.5
	github.com/lib/pq v1.10.9
	github.com/voice-cloning/shared v0.0.0-00010101000000-000000000000
)


