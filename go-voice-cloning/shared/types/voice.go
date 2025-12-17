package types

import "time"

// VoiceClone represents a voice cloning job
type VoiceClone struct {
	ID          int       `json:"id" db:"id"`
	UserID      int       `json:"user_id" db:"user_id"`
	Name        string    `json:"name" db:"name"`
	Status      string    `json:"status" db:"status"` // pending, processing, completed, failed
	SourceFile  string    `json:"source_file" db:"source_file"`
	OutputFile  string    `json:"output_file,omitempty" db:"output_file"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
	CompletedAt *time.Time `json:"completed_at,omitempty" db:"completed_at"`
}

// VoiceCloneRequest represents a request to create a voice clone
type VoiceCloneRequest struct {
	Name       string `json:"name" validate:"required"`
	SourceFile string `json:"source_file" validate:"required"`
}

// VoiceCloneResponse represents the response after creating a voice clone job
type VoiceCloneResponse struct {
	ID     int    `json:"id"`
	Status string `json:"status"`
	Message string `json:"message"`
}


