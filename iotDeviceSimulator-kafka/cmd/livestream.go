package main 

import(
	"net/http"
	
	"log"
	
	"bytes"
	"encoding/base64"
	"time"
)

func pushFrame(endpoint string, url string){
	log.Println("Fetching file index.m3u8", url)
	
	client := &http.Client{}

	buf := new(bytes.Buffer)
	for {
		resp, err := http.Get(url)
		if err != nil {
			log.Fatal(err)
		}
		//
		defer resp.Body.Close()

		buf.ReadFrom(resp.Body)
		
		imgBase64Str := base64.StdEncoding.EncodeToString(buf.Bytes())
		
		
		buf.ReadFrom(resp.Body)


		var payload = []byte(`{"records":[{"key":"key1","value":"` + imgBase64Str + `"}]}`)
		
		resp.Body.Close()
		buf.Reset()
		imgBase64Str = ""
		
		//NORMAL HTTP 
		req, err := http.NewRequest("POST", "http://" + endpoint,  bytes.NewBuffer(payload))
		if err != nil {
			log.Fatalln(err)
		}
		
        	req.Header.Set("Content-Type", "application/vnd.kafka.json.v2+json")
		log.Println("Sending IoT Video to Kafka bridge")
		resp, err = client.Do(req)
		if err != nil {
			log.Fatalln(err)
		}
		defer resp.Body.Close()
		
		time.Sleep(20* time.Second)

    }
}
