package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gorilla/mux"
	
	"github.com/voice-cloning/shared/utils"
)

type StorageService struct {
	storagePath string
}

func main() {
	storagePath := os.Getenv("STORAGE_PATH")
	if storagePath == "" {
		storagePath = "./storage"
	}

	// Create storage directory if it doesn't exist
	if err := os.MkdirAll(storagePath, 0755); err != nil {
		log.Fatal("Failed to create storage directory:", err)
	}

	service := &StorageService{storagePath: storagePath}

	// Setup routes
	r := mux.NewRouter()
	r.HandleFunc("/health", healthCheck).Methods("GET")
	r.HandleFunc("/upload", service.uploadFile).Methods("POST")
	r.HandleFunc("/download/{filename}", service.downloadFile).Methods("GET")
	r.HandleFunc("/files/{filename}", service.deleteFile).Methods("DELETE")
	r.HandleFunc("/files", service.listFiles).Methods("GET")

	port := os.Getenv("PORT")
	if port == "" {
		port = "8083"
	}

	log.Printf("Storage Service starting on port %s", port)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func healthCheck(w http.ResponseWriter, r *http.Request) {
	utils.JSONResponse(w, http.StatusOK, map[string]string{
		"status": "healthy",
		"service": "storage-service",
	})
}

func (s *StorageService) uploadFile(w http.ResponseWriter, r *http.Request) {
	// Parse multipart form
	err := r.ParseMultipartForm(10 << 20) // 10 MB max
	if err != nil {
		utils.ErrorResponse(w, http.StatusBadRequest, "Failed to parse form")
		return
	}

	file, handler, err := r.FormFile("file")
	if err != nil {
		utils.ErrorResponse(w, http.StatusBadRequest, "No file provided")
		return
	}
	defer file.Close()

	// Create file path
	filePath := filepath.Join(s.storagePath, handler.Filename)

	// Create file
	dst, err := os.Create(filePath)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to save file")
		return
	}
	defer dst.Close()

	// Copy file content
	_, err = io.Copy(dst, file)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to save file")
		return
	}

	utils.JSONResponse(w, http.StatusOK, map[string]interface{}{
		"filename": handler.Filename,
		"size":     handler.Size,
		"path":     filePath,
		"message":  "File uploaded successfully",
	})
}

func (s *StorageService) downloadFile(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	filename := vars["filename"]

	filePath := filepath.Join(s.storagePath, filename)

	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		utils.ErrorResponse(w, http.StatusNotFound, "File not found")
		return
	}

	// Open file
	file, err := os.Open(filePath)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to open file")
		return
	}
	defer file.Close()

	// Set headers
	w.Header().Set("Content-Type", "application/octet-stream")
	w.Header().Set("Content-Disposition", fmt.Sprintf("attachment; filename=%s", filename))

	// Copy file to response
	io.Copy(w, file)
}

func (s *StorageService) deleteFile(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	filename := vars["filename"]

	filePath := filepath.Join(s.storagePath, filename)

	// Check if file exists
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		utils.ErrorResponse(w, http.StatusNotFound, "File not found")
		return
	}

	// Delete file
	err := os.Remove(filePath)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to delete file")
		return
	}

	utils.JSONResponse(w, http.StatusOK, map[string]string{
		"message": "File deleted successfully",
	})
}

func (s *StorageService) listFiles(w http.ResponseWriter, r *http.Request) {
	files, err := os.ReadDir(s.storagePath)
	if err != nil {
		utils.ErrorResponse(w, http.StatusInternalServerError, "Failed to list files")
		return
	}

	var fileList []map[string]interface{}
	for _, file := range files {
		if !file.IsDir() {
			info, err := file.Info()
			if err != nil {
				continue
			}
			fileList = append(fileList, map[string]interface{}{
				"name": file.Name(),
				"size": info.Size(),
			})
		}
	}

	utils.SuccessResponse(w, fileList)
}


