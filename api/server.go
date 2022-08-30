package main

import (
	"database/sql"

	"github.com/gorilla/mux"
)

type Server struct {
	Router *mux.Router
	DB     *sql.DB
	Groups []string
}

func (s *Server) connectToDB(name string) (err error) {
	s.DB, err = sql.Open("sqlite3", name)
	return
}
