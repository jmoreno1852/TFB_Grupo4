extends Node2D

@onready var http_request_guilds = $HTTPRequestGuilds

var guilds: Array = []

func _ready():
	http_request_guilds.request_completed.connect(_on_guilds_loaded)
	load_guilds()

func load_guilds():
	var url = Global.url + "guilds"
	var headers = [
		"Authorization: Bearer " + Global.userToken
	]
	http_request_guilds.request(
		url,
		headers,
		HTTPClient.METHOD_GET
	)

func _on_guilds_loaded(result, response_code, headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	var json = JSON.new()
	if json.parse(body.get_string_from_utf8()) != OK:
		return
	var response = json.get_data()
	if response.has("guilds"):
		guilds = response["guilds"]
		%GuildComponent.setup(guilds)

func join_guild(guild_id: String):
	var url = Global.url + "guilds/join"
	var headers = [
		"Authorization: Bearer " + Global.userToken,
		"Content-Type: application/json"
	]
	var body = JSON.stringify({
		"guild_id": guild_id
	})
	http_request_guilds.request(
		url,
		headers,
		HTTPClient.METHOD_POST,
		body
	)
	
func leave_guild(guild_id: String):
	var url = Global.url + "guilds/leave"
	var headers = [
		"Authorization: Bearer " + Global.userToken,
		"Content-Type: application/json"
	]
	var body = JSON.stringify({
		"guild_id": guild_id
	})
	http_request_guilds.request(
		url,
		headers,
		HTTPClient.METHOD_POST,
		body
	)
	

func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main.tscn")
