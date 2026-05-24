extends Node

@onready var http_request = HTTPRequest.new()

func _ready():
	add_child(http_request)
	http_request.request_completed.connect(_on_http_request_completed)
	
func load_progression():
	var url = Global.url + "progression/me"
	var headers = [
		"Authorization: Bearer " + Global.userToken
	]
	http_request.request(url, headers, HTTPClient.METHOD_GET)

func _on_http_request_completed(result, response_code, headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		return

	var json = JSON.new()
	var parse_error = json.parse(body.get_string_from_utf8())

	if parse_error != OK:
		return

	var response = json.get_data()

	if response.has("progression"):
		var p = response["progression"]

		Global.gold = p.get("gold", 0)
		Global.level = p.get("level", 0)
		Global.xp = p.get("xp", 0)
		Global.stats = p.get("stats", {})
