from prometheus_client import Counter, Histogram

request_counter = Counter("chatbot_requests_total", "Total number of chatbot requests", ["endpoint"])
response_time_histogram = Histogram("chatbot_response_time_seconds", "Response time of chatbot requests", ["endpoint"])