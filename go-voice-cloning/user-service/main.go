package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/mux"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	
	"github.com/voice-cloning/shared/types"
	"github.com/voice-cloning/shared/utils"
)

type UserService struct {
	db *sqlx.DB
}

func main() {
	// Database connection
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://postgres:postgres@localhost:5432/voice_cloning?sslmode=disable"
	}

	db, err := sqlx.Connect("postgres", dbURL)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer db.Close()

	// Initialize database schema
	initDB(db)

	service := &UserService{db: db}

	// Setup routes
	r := mux.NewRouter()
	r.HandleFunc("/health", healthCheck).Methods("GET")
	r.HandleFunc("/profile", service.getProfile).Methods("GET")
	r.HandleFunc("/profile", service.updateProfile).Methods("PUT")
	r.HandleFunc("/stats", service.getStats).Methods("GET")

	port := os.Getenv("PORT")
	if port == "" {
		port = "8084"
	}

	log.Printf("User Service starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	utils.JSONResponse(w, http.StatusOK, map[string]string{
		"status": "healthy",
		"service": "user-service",
	})
}

func getUserID(r *http.Request) int {
	userID := r.Header.Get("X-User-ID")
	if userID == "" {
		return 0
	}
	var id int
	_, err := fmt.Sscanf(userID, "%d", &id)
	if err != nil {
		return 0
	}
	return id
}

func (s *UserService) getProfile(w http.ResponseWriter, r *http.Request) {
	userID := getUserID(r)
	if userID == 0 {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Unauthorized")
		return
	}

	var profile types.UserProfile
	err := s.db.Get(&profile,
		`SELECT u.id, u.email, u.username, u.created_at, u.updated_at,
			COALESCE(up.first_name, '') as first_name,
			COALESCE(up.last_name, '') as last_name,
			COALESCE(up.bio, '') as bio
		FROM users u
		LEFT JOIN user_profiles up ON u.id = up.user_id
		WHERE u.id = $1`,
		userID)

	if err != nil {
		utils.ErrorResponse(w, http.StatusNotFound, "User not found")
		return
	}

	utils.SuccessResponse(w, profile)
}

func (s *UserService) updateProfile(w http.ResponseWriter, r *http.Request) {
	userID := getUserID(r)
	if userID == 0 {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Unauthorized")
		return
	}

	var req struct {
		FirstName string `json:"first_name"`
		LastName  string `json:"last_name"`
		Bio       string `json:"bio"`
	}

	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.ErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	// Upsert user profile
	s.db.MustExec(
		`INSERT INTO user_profiles (user_id, first_name, last_name, bio, updated_at)
		VALUES ($1, $2, $3, $4, $5)
		ON CONFLICT (user_id) DO UPDATE SET
			first_name = EXCLUDED.first_name,
			last_name = EXCLUDED.last_name,
			bio = EXCLUDED.bio,
			updated_at = EXCLUDED.updated_at`,
		userID, req.FirstName, req.LastName, req.Bio, time.Now())

	utils.SuccessResponse(w, map[string]string{"message": "Profile updated successfully"})
}

func (s *UserService) getStats(w http.ResponseWriter, r *http.Request) {
	userID := getUserID(r)
	if userID == 0 {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Unauthorized")
		return
	}

	var stats struct {
		TotalClones      int `json:"total_clones" db:"total_clones"`
		CompletedClones  int `json:"completed_clones" db:"completed_clones"`
		PendingClones    int `json:"pending_clones" db:"pending_clones"`
		ProcessingClones int `json:"processing_clones" db:"processing_clones"`
	}

	err := s.db.Get(&stats,
		`SELECT 
			COUNT(*) as total_clones,
			COUNT(*) FILTER (WHERE status = 'completed') as completed_clones,
			COUNT(*) FILTER (WHERE status = 'pending') as pending_clones,
			COUNT(*) FILTER (WHERE status = 'processing') as processing_clones
		FROM voice_clones
		WHERE user_id = $1`,
		userID)

	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to fetch stats")
		return
	}

	utils.SuccessResponse(w, stats)
}

func initDB(db *sqlx.DB) {
	schema := `
	CREATE TABLE IF NOT EXISTS user_profiles (
		user_id INTEGER PRIMARY KEY,
		first_name VARCHAR(100),
		last_name VARCHAR(100),
		bio TEXT,
		updated_at TIMESTAMP NOT NULL,
		FOREIGN KEY (user_id) REFERENCES users(id)
	);
	`
	db.MustExec(schema)
	log.Println("User service database schema initialized")
}

