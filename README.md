# otel-playground
Local stack to test features of the opentelemetry collector. 

### endpoints
http://localhost:8000/ base API endpoint  
http://localhost:8000/process/{item_id} dummy endpoint to mock kafka read + db write  
http://localhost:3000/ Grafana LGTM frontend  

### data flow
```
app -> otel-collector -> lgtm stack
```
