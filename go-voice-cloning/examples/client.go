package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
)

const baseURL = "http://localhost:8080"

func main() {
	fmt.Println("Voice Cloning API Client Example")
	fmt.Println("================================\n")

	// 1. Register a new user
	fmt.Println("1. Registering user...")
	registerResp, err := register("test@example.com", "testuser", "password123")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Registered! Token: %s\n\n", registerResp.Token[:50]+"...")

	// 2. Create a voice clone
	fmt.Println("2. Creating voice clone...")
	cloneResp, err := createVoiceClone(registerResp.Token, "My First Clone", "audio/sample.wav")
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Created clone ID: %d, Status: %s\n\n", cloneResp.ID, cloneResp.Status)

	// 3. Check clone status
	fmt.Println("3. Checking clone status...")
	status, err := getCloneStatus(registerResp.Token, cloneResp.ID)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Status: %s\n\n", status)

	// 4. List all clones
	fmt.Println("4. Listing all clones...")
	clones, err := listClones(registerResp.Token)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Total clones: %d\n\n", len(clones))

	// 5. Get user profile
	fmt.Println("5. Getting user profile...")
	profile, err := getUserProfile(registerResp.Token)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Profile: %s (%s)\n\n", profile.Username, profile.Email)

	// 6. Get user stats
	fmt.Println("6. Getting user stats...")
	stats, err := getUserStats(registerResp.Token)
	if err != nil {
		fmt.Printf("Error: %v\n", err)
		return
	}
	fmt.Printf("Stats: %+v\n", stats)
}

type RegisterResponse struct {
	Token     string `json:"token"`
	ExpiresAt string `json:"expires_at"`
	User      struct {
		ID       int    `json:"id"`
		Email    string `json:"email"`
		Username string `json:"username"`
	} `json:"user"`
}

type CloneResponse struct {
	ID      int    `json:"id"`
	Status  string `json:"status"`
	Message string `json:"message"`
}

type Clone struct {
	ID        int    `json:"id"`
	Name      string `json:"name"`
	Status    string `json:"status"`
	CreatedAt string `json:"created_at"`
}

type Profile struct {
	ID       int    `json:"id"`
	Email    string `json:"email"`
	Username string `json:"username"`
}

type Stats struct {
	TotalClones      int `json:"total_clones"`
	CompletedClones  int `json:"completed_clones"`
	PendingClones    int `json:"pending_clones"`
	ProcessingClones int `json:"processing_clones"`
}

func register(email, username, password string) (*RegisterResponse, error) {
	reqBody := map[string]string{
		"email":    email,
		"username": username,
		"password": password,
	}
	jsonData, _ := json.Marshal(reqBody)

	resp, err := http.Post(baseURL+"/api/auth/register", "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result RegisterResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

func createVoiceClone(token, name, sourceFile string) (*CloneResponse, error) {
	reqBody := map[string]string{
		"name":       name,
		"source_file": sourceFile,
	}
	jsonData, _ := json.Marshal(reqBody)

	req, _ := http.NewRequest("POST", baseURL+"/api/voice/clones", bytes.NewBuffer(jsonData))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result CloneResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

func getCloneStatus(token string, cloneID int) (string, error) {
	req, _ := http.NewRequest("GET", fmt.Sprintf("%s/api/voice/clones/%d/status", baseURL, cloneID), nil)
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var result struct {
		Status string `json:"status"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", err
	}

	return result.Status, nil
}

func listClones(token string) ([]Clone, error) {
	req, _ := http.NewRequest("GET", baseURL+"/api/voice/clones", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var clones []Clone
	if err := json.NewDecoder(resp.Body).Decode(&clones); err != nil {
		return nil, err
	}

	return clones, nil
}

func getUserProfile(token string) (*Profile, error) {
	req, _ := http.NewRequest("GET", baseURL+"/api/user/profile", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var profile Profile
	if err := json.NewDecoder(resp.Body).Decode(&profile); err != nil {
		return nil, err
	}

	return &profile, nil
}

func getUserStats(token string) (*Stats, error) {
	req, _ := http.NewRequest("GET", baseURL+"/api/user/stats", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var stats Stats
	if err := json.NewDecoder(resp.Body).Decode(&stats); err != nil {
		return nil, err
	}

	return &stats, nil
}

func uploadFile(token, filePath string) error {
	file, err := os.Open(filePath)
	if err != nil {
		return err
	}
	defer file.Close()

	var requestBody bytes.Buffer
	writer := multipart.NewWriter(&requestBody)
	part, err := writer.CreateFormFile("file", filePath)
	if err != nil {
		return err
	}

	io.Copy(part, file)
	writer.Close()

	req, _ := http.NewRequest("POST", baseURL+"/api/storage/upload", &requestBody)
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	return nil
}


