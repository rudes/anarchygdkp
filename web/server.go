package main

import (
	"log"
	"net/http"
)

const (
	TEMPLATE_ROOT = "/app/templates/"
)

func main() {
	http.HandleFunc("/", home)
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func home(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, TEMPLATE_ROOT+"home.tmpl")
}
