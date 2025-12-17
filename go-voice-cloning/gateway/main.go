package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strings"

	"github.com/gorilla/mux"
	
	"github.com/voice-cloning/shared/utils"
)

type Gateway struct {
	authServiceURL   string
	voiceServiceURL  string
	storageServiceURL string
	userServiceURL   string
}

func main() {
	gateway := &Gateway{
		authServiceURL:    getEnv("AUTH_SERVICE_URL", "http://localhost:8081"),
		voiceServiceURL:   getEnv("VOICE_SERVICE_URL", "http://localhost:8082"),
		storageServiceURL: getEnv("STORAGE_SERVICE_URL", "http://localhost:8083"),
		userServiceURL:    getEnv("USER_SERVICE_URL", "http://localhost:8084"),
	}

	r := mux.NewRouter()

	// Health check
	r.HandleFunc("/health", healthCheck).Methods("GET")

	// Public routes (no auth required)
	r.HandleFunc("/api/auth/register", gateway.proxyToAuth).Methods("POST")
	r.HandleFunc("/api/auth/login", gateway.proxyToAuth).Methods("POST")

	// Protected routes (auth required)
	protected := r.PathPrefix("/api").Subrouter()
	protected.Use(gateway.authMiddleware)
	protected.HandleFunc("/voice/clones", gateway.proxyToVoice).Methods("GET", "POST")
	protected.HandleFunc("/voice/clones/{id}", gateway.proxyToVoice).Methods("GET")
	protected.HandleFunc("/voice/clones/{id}/status", gateway.proxyToVoice).Methods("GET")
	protected.HandleFunc("/storage/upload", gateway.proxyToStorage).Methods("POST")
	protected.HandleFunc("/storage/download/{filename}", gateway.proxyToStorage).Methods("GET")
	protected.HandleFunc("/storage/files", gateway.proxyToStorage).Methods("GET")
	protected.HandleFunc("/storage/files/{filename}", gateway.proxyToStorage).Methods("DELETE")
	protected.HandleFunc("/user/profile", gateway.proxyToUser).Methods("GET", "PUT")
	protected.HandleFunc("/user/stats", gateway.proxyToUser).Methods("GET")

	port := getEnv("PORT", "8080")
	log.Printf("API Gateway starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	utils.JSONResponse(w, http.StatusOK, map[string]string{
		"status": "healthy",
		"service": "api-gateway",
	})
}

// Auth middleware validates JWT token and adds user ID to header
func (g *Gateway) authMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		authHeader := r.Header.Get("Authorization")
		if authHeader == "" {
			utils.ErrorResponse(w, http.StatusUnauthorized, "Missing authorization header")
			return
		}

		// Extract token
		parts := strings.Split(authHeader, " ")
		if len(parts) != 2 || parts[0] != "Bearer" {
			utils.ErrorResponse(w, http.StatusUnauthorized, "Invalid authorization header format")
			return
		}

		token := parts[1]

		// Validate token with auth service
		claims, err := validateTokenWithAuthService(g.authServiceURL, token)
		if err != nil {
			utils.ErrorResponse(w, http.StatusUnauthorized, "Invalid token")
			return
		}

		// Add user ID to header for downstream services
		r.Header.Set("X-User-ID", fmt.Sprintf("%d", claims.UserID))
		r.Header.Set("X-User-Email", claims.Email)
		r.Header.Set("X-User-Username", claims.Username)

		next.ServeHTTP(w, r)
	})
}

func validateTokenWithAuthService(authServiceURL, token string) (*utils.Claims, error) {
	reqBody := map[string]string{"token": token}
	jsonData, _ := json.Marshal(reqBody)

	resp, err := http.Post(authServiceURL+"/validate", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("token validation failed")
	}

	var result struct {
		Valid  bool         `json:"valid"`
		Claims utils.Claims `json:"claims"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	if !result.Valid {
		return nil, fmt.Errorf("invalid token")
	}

	return &result.Claims, nil
}

// Proxy handlers
func (g *Gateway) proxyToAuth(w http.ResponseWriter, r *http.Request) {
	proxyRequest(w, r, g.authServiceURL, func(path string) string {
		// /api/auth/register -> /register, /api/auth/login -> /login
		return strings.TrimPrefix(path, "/api/auth")
	})
}

func (g *Gateway) proxyToVoice(w http.ResponseWriter, r *http.Request) {
	proxyRequest(w, r, g.voiceServiceURL, func(path string) string {
		// /api/voice/clones -> /clones
		return strings.TrimPrefix(path, "/api/voice")
	})
}

func (g *Gateway) proxyToStorage(w http.ResponseWriter, r *http.Request) {
	proxyRequest(w, r, g.storageServiceURL, func(path string) string {
		// /api/storage/upload -> /upload
		return strings.TrimPrefix(path, "/api/storage")
	})
}

func (g *Gateway) proxyToUser(w http.ResponseWriter, r *http.Request) {
	proxyRequest(w, r, g.userServiceURL, func(path string) string {
		// /api/user/profile -> /profile
		return strings.TrimPrefix(path, "/api/user")
	})
}

func proxyRequest(w http.ResponseWriter, r *http.Request, targetBaseURL string, pathMapper func(string) string) {
	// Parse target URL
	targetURL, err := url.Parse(targetBaseURL)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Invalid target URL")
		return
	}

	// Create reverse proxy
	proxy := httputil.NewSingleHostReverseProxy(targetURL)

	// Modify request path
	originalPath := r.URL.Path
	servicePath := pathMapper(originalPath)
	r.URL.Path = servicePath

	// Preserve query parameters
	r.URL.RawQuery = r.URL.Query().Encode()

	// Set target host
	r.URL.Host = targetURL.Host
	r.URL.Scheme = targetURL.Scheme
	r.Host = targetURL.Host

	// Create a custom director
	originalDirector := proxy.Director
	proxy.Director = func(req *http.Request) {
		originalDirector(req)
		req.URL.Host = targetURL.Host
		req.URL.Scheme = targetURL.Scheme
	}

	// Serve request
	proxy.ServeHTTP(w, r)
}

