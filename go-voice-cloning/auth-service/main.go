package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gorilla/mux"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"golang.org/x/crypto/bcrypt"
	
	"github.com/voice-cloning/shared/types"
	"github.com/voice-cloning/shared/utils"
)

type AuthService struct {
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

	service := &AuthService{db: db}

	// Setup routes
	r := mux.NewRouter()
	r.HandleFunc("/health", healthCheck).Methods("GET")
	r.HandleFunc("/register", service.register).Methods("POST")
	r.HandleFunc("/login", service.login).Methods("POST")
	r.HandleFunc("/validate", service.validateToken).Methods("POST")

	port := os.Getenv("PORT")
	if port == "" {
		port = "8081"
	}

	log.Printf("Auth Service starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	utils.JSONResponse(w, http.StatusOK, map[string]string{
		"status": "healthy",
		"service": "auth-service",
	})
}

func (s *AuthService) register(w http.ResponseWriter, r *http.Request) {
	var req types.RegisterRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.ErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	// Check if user already exists
	var existingID int
	err := s.db.Get(&existingID, "SELECT id FROM users WHERE email = $1 OR username = $2", req.Email, req.Username)
	if err == nil {
		utils.ErrorResponse(w, http.StatusConflict, "User already exists")
		return
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to hash password")
		return
	}

	// Insert user
	var userID int
	err = s.db.QueryRow(
		"INSERT INTO users (email, username, password, created_at, updated_at) VALUES ($1, $2, $3, $4, $5) RETURNING id",
		req.Email, req.Username, string(hashedPassword), time.Now(), time.Now(),
	).Scan(&userID)

	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to create user")
		return
	}

	// Generate token
	token, err := utils.GenerateToken(userID, req.Email, req.Username)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to generate token")
		return
	}

	user := types.User{
		ID:        userID,
		Email:     req.Email,
		Username:  req.Username,
		CreatedAt: time.Now(),
		UpdatedAt: time.Now(),
	}

	utils.JSONResponse(w, http.StatusCreated, types.AuthResponse{
		Token:     token,
		ExpiresAt: time.Now().Add(24 * time.Hour),
		User:      user,
	})
}

func (s *AuthService) login(w http.ResponseWriter, r *http.Request) {
	var req types.LoginRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.ErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	// Get user from database
	var user types.User
	err := s.db.Get(&user, "SELECT id, email, username, password, created_at, updated_at FROM users WHERE email = $1", req.Email)
	if err != nil {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Invalid credentials")
		return
	}

	// Verify password
	err = bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password))
	if err != nil {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Invalid credentials")
		return
	}

	// Generate token
	token, err := utils.GenerateToken(user.ID, user.Email, user.Username)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to generate token")
		return
	}

	// Clear password before sending response
	user.Password = ""

	utils.JSONResponse(w, http.StatusOK, types.AuthResponse{
		Token:     token,
		ExpiresAt: time.Now().Add(24 * time.Hour),
		User:      user,
	})
}

func (s *AuthService) validateToken(w http.ResponseWriter, r *http.Request) {
	var req struct {
		Token string `json:"token"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		utils.ErrorResponse(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	claims, err := utils.ValidateToken(req.Token)
	if err != nil {
		utils.ErrorResponse(w, http.StatusUnauthorized, "Invalid token")
		return
	}

	utils.JSONResponse(w, http.StatusOK, map[string]interface{}{
		"valid": true,
		"claims": claims,
	})
}

func initDB(db *sqlx.DB) {
	schema := `
	CREATE TABLE IF NOT EXISTS users (
		id SERIAL PRIMARY KEY,
		email VARCHAR(255) UNIQUE NOT NULL,
		username VARCHAR(100) UNIQUE NOT NULL,
		password VARCHAR(255) NOT NULL,
		created_at TIMESTAMP NOT NULL,
		updated_at TIMESTAMP NOT NULL
	);
	`
	db.MustExec(schema)
	log.Println("Database schema initialized")
}


