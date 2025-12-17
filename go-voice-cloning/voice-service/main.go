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

type VoiceService struct {
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

	service := &VoiceService{db: db}

	// Setup routes
	r := mux.NewRouter()
	r.HandleFunc("/health", healthCheck).Methods("GET")
	r.HandleFunc("/clones", service.createClone).Methods("POST")
	r.HandleFunc("/clones/{id}", service.getClone).Methods("GET")
	r.HandleFunc("/clones", service.listClones).Methods("GET")
	r.HandleFunc("/clones/{id}/status", service.getStatus).Methods("GET")

	port := os.Getenv("PORT")
	if port == "" {
		port = "8082"
	}

	log.Printf("Voice Service starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	utils.JSONResponse(w, http.StatusOK, map[string]string{
		"status": "healthy",
		"service": "voice-service",
	})
}

// Middleware to extract user ID from token (simplified - in production, validate token)
func getUserID(r *http.Request) int {
	// In a real implementation, extract and validate JWT token
	// For now, we'll get it from a header set by the gateway
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

func (s *VoiceService) createClone(w http.ResponseWriter, r *http.Request) {
	userID := getUserID(r)
	if userID == 0 {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Unauthorized")
		return
	}

	var req types.VoiceCloneRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.ErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	// Create voice clone record
	var cloneID int
	err := s.db.QueryRow(
		"INSERT INTO voice_clones (user_id, name, status, source_file, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
		userID, req.Name, "pending", req.SourceFile, time.Now(), time.Now(),
	).Scan(&cloneID)

	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to create voice clone")
		return
	}

	// In a real implementation, this would trigger async processing
	// For now, we'll simulate it by updating status after a delay
	go s.processVoiceClone(cloneID)

	utils.JSONResponse(w, http.StatusCreated, types.VoiceCloneResponse{
		ID:      cloneID,
		Status:  "pending",
		Message: "Voice clone job created",
	})
}

func (s *VoiceService) getClone(w http.ResponseWriter, r *http.Request) {
	userID := getUserID(r)
	if userID == 0 {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Unauthorized")
		return
	}

	vars := mux.Vars(r)
	cloneID := vars["id"]

	var clone types.VoiceClone
	err := s.db.Get(&clone, 
		"SELECT id, user_id, name, status, source_file, output_file, created_at, updated_at, completed_at FROM voice_clones WHERE id = $1 AND user_id = $2",
		cloneID, userID)

	if err != nil {
		utils.ErrorResponse(w, http.StatusNotFound, "Voice clone not found")
		return
	}

	utils.SuccessResponse(w, clone)
}

func (s *VoiceService) listClones(w http.ResponseWriter, r *http.Request) {
	userID := getUserID(r)
	if userID == 0 {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Unauthorized")
		return
	}

	var clones []types.VoiceClone
	err := s.db.Select(&clones,
		"SELECT id, user_id, name, status, source_file, output_file, created_at, updated_at, completed_at FROM voice_clones WHERE user_id = $1 ORDER BY created_at DESC",
		userID)

	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to fetch voice clones")
		return
	}

	utils.SuccessResponse(w, clones)
}

func (s *VoiceService) getStatus(w http.ResponseWriter, r *http.Request) {
	userID := getUserID(r)
	if userID == 0 {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Unauthorized")
		return
	}

	vars := mux.Vars(r)
	cloneID := vars["id"]

	var status string
	err := s.db.Get(&status,
		"SELECT status FROM voice_clones WHERE id = $1 AND user_id = $2",
		cloneID, userID)

	if err != nil {
		utils.ErrorResponse(w, http.StatusNotFound, "Voice clone not found")
		return
	}

	utils.SuccessResponse(w, map[string]string{"status": status})
}

func (s *VoiceService) processVoiceClone(cloneID int) {
	// Simulate processing time
	time.Sleep(5 * time.Second)

	// Update status to processing
	s.db.MustExec("UPDATE voice_clones SET status = $1, updated_at = $2 WHERE id = $3",
		"processing", time.Now(), cloneID)

	// Simulate more processing
	time.Sleep(10 * time.Second)

	// Update status to completed
	completedAt := time.Now()
	s.db.MustExec("UPDATE voice_clones SET status = $1, output_file = $2, updated_at = $3, completed_at = $4 WHERE id = $5",
		"completed", fmt.Sprintf("output/clone_%d.wav", cloneID), time.Now(), completedAt, cloneID)

	log.Printf("Voice clone %d processing completed", cloneID)
}

func initDB(db *sqlx.DB) {
	schema := `
	CREATE TABLE IF NOT EXISTS voice_clones (
		id SERIAL PRIMARY KEY,
		user_id INTEGER NOT NULL,
		name VARCHAR(255) NOT NULL,
		status VARCHAR(50) NOT NULL,
		source_file VARCHAR(500) NOT NULL,
		output_file VARCHAR(500),
		created_at TIMESTAMP NOT NULL,
		updated_at TIMESTAMP NOT NULL,
		completed_at TIMESTAMP,
		FOREIGN KEY (user_id) REFERENCES users(id)
	);
	`
	db.MustExec(schema)
	log.Println("Voice service database schema initialized")
}

