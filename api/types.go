package main

import (
	"time"
)

type Place struct {
	Building string `json:"building"`
	Room     string `json:"room"`
}

type Lecturer struct {
	Name  string `json:"name"`
	Title string `json:"title"`
}

type Class struct {
	Name        string    `json:"subject"`
	Lecturer    Lecturer  `json:"lecturer"`
	Beginning   time.Time `json:"beginning"`
	End         time.Time `json:"end"`
	Place       Place     `json:"place"`
	LectureType string    `json:"type"`
	Group       string    `json:"rawGroup"`
}

type SuccessResponse struct {
	Classes []Class `json:"classes"`
}

type ErrorResponse struct {
	Reason string `json:"reason"`
}
