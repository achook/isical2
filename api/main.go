package main

import (
	"encoding/json"
	"errors"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
	_ "github.com/mattn/go-sqlite3"
)

func handleBackendError(err error) {
	if err != nil {
		log.Println(err)
	}
}

func handleFatalBackendError(err error) {
	if err != nil {
		log.Fatalln(err)
	}
}

func handleFrontendError(w http.ResponseWriter, err error, reason string, code int) {
	if err != nil {
		r := ErrorResponse{}
		r.Reason = reason

		e, err2 := json.Marshal(r)
		if err2 != nil {
			handleBackendError(err2)
		}

		handleBackendError(err)
		http.Error(w, string(e), code)
	}

}

func handleUnconditionalFrontendError(w http.ResponseWriter, reason string, code int) {
	r := ErrorResponse{}
	r.Reason = reason

	e, err2 := json.Marshal(r)
	if err2 != nil {
		handleBackendError(err2)
	}

	http.Error(w, string(e), code)
}

func (s *Server) getAllowedGroups() (err error) {
	rows, err := s.DB.Query("SELECT DISTINCT group_name FROM mappings")
	if err != nil {
		return err
	}

	s.Groups = make([]string, 0)

	for rows.Next() {
		var g string
		rows.Scan(&g)
		s.Groups = append(s.Groups, g)
	}

	return nil
}

func (s *Server) isCorrectGroup(group string) bool {
	for _, g := range s.Groups {
		if g == group {
			return true
		}
	}
	return false
}

func (s *Server) handleSingle(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	group := vars["group"]

	stmt, err := s.DB.Prepare(`SELECT classes.start, classes.end,
								  classes.subject, classes.class_group,
								  classes.building, classes.room,
								  classes.class_type,
								  lecturers.name, lecturers.title,
								  mappings.group_name
						   FROM classes
                		   INNER JOIN mappings ON classes.subject = mappings.class_name AND
                                        	      classes.class_group = mappings.class_group
                		   LEFT JOIN lecturers on classes.lecturer_id = lecturers.id
						   WHERE group_name = ?`)

	handleFrontendError(w, err, "Internal database error", http.StatusInternalServerError)

	if !s.isCorrectGroup(group) {
		handleUnconditionalFrontendError(w, "Selected group doesn't exist", http.StatusBadRequest)
	}

	rows, err := stmt.Query(group)
	handleFrontendError(w, err, "Internal database error", http.StatusInternalServerError)

	var classes []Class

	for rows.Next() {
		p := Place{}
		c := Class{}
		l := Lecturer{}

		var gr string

		rows.Scan(&c.Beginning, &c.End, &c.Name, &c.Group, &p.Building, &p.Room, &c.LectureType, &l.Name, &l.Title, &gr)

		c.Place = p
		c.Lecturer = l

		classes = append(classes, c)
	}

	err = json.NewEncoder(w).Encode(classes)
	handleFrontendError(w, err, "Internal database error", http.StatusInternalServerError)
}

func (s *Server) handleAll(w http.ResponseWriter, r *http.Request) {
	rows, err := s.DB.Query(`SELECT classes.start, classes.end,
								  classes.subject, classes.class_group,
								  classes.building, classes.room,
								  classes.class_type,
								  lecturers.name, lecturers.title,
								  mappings.group_name
						   FROM classes
                		   INNER JOIN mappings ON classes.subject = mappings.class_name AND
                                        	      classes.class_group = mappings.class_group
                		   LEFT JOIN lecturers on classes.lecturer_id = lecturers.id`)

	handleFrontendError(w, err, "Internal database error", http.StatusInternalServerError)

	var classes []Class

	for rows.Next() {
		p := Place{}
		c := Class{}
		l := Lecturer{}

		var gr string

		rows.Scan(&c.Beginning, &c.End, &c.Name, &c.Group, &p.Building, &p.Room, &c.LectureType, &l.Name, &l.Title, &gr)

		c.Place = p
		c.Lecturer = l

		classes = append(classes, c)
	}

	err = json.NewEncoder(w).Encode(classes)
	handleFrontendError(w, err, "Internal database error", http.StatusInternalServerError)
}

func main() {
	s := Server{}

	dbPath, ok := os.LookupEnv("DB_PATH")
	if !ok || dbPath == "" {
		handleBackendError(errors.New("DB_PATH env var is not set or is empty"))
	}

	err := s.connectToDB(dbPath)
	handleFatalBackendError(err)

	s.Router = mux.NewRouter()

	err = s.getAllowedGroups()
	handleFatalBackendError(err)

	s.Router.HandleFunc("/all", s.handleAll)
	s.Router.HandleFunc("/{group}", s.handleSingle)

	log.Fatal(http.ListenAndServe(":8080", s.Router))
}
