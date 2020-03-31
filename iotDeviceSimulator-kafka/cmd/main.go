package main


import (
	
	"os"
	"os/exec"
	"log"
	"strings"
)

func main() { 
	//Must Set environment var STREAMURL 
	urlpage := os.Getenv("STREAMURL")
	
	log.Println(urlpage)
	url,err := exec.Command("youtube-dl","-g",urlpage).Output()
	if err != nil {
        log.Fatal(err)
    }	

	for{
	
	//Must Set Env Var Endpoint to direct IoT simulation to a Messaging Endpoint 
	
	endpoint := os.Getenv("ENDPOINT")
	pushFrame(endpoint,strings.TrimSpace(string(url)))

	}
}	
