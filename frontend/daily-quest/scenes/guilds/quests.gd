extends Node2D

@onready var http_request = $HTTPRequestQuests
var quests: Array = []

func _ready():
	http_request.request_completed.connect(
		_on_http_request_completed
	)
	load_quests()

func load_quests():
	var url = Global.url + "quests"
	var headers = [
		"Authorization: Bearer "
		+ Global.userToken
	]
	http_request.request(url,headers,HTTPClient.METHOD_GET)

func _on_http_request_completed(result,response_code,headers,body):
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	var json = JSON.new()
	if json.parse(body.get_string_from_utf8()) != OK:
		return
	var response = json.get_data()
	if response.has("quests"):
		quests = response["quests"]
		%QuestComponent.setup(quests)

func complete_quest(quest_id: String):
	var url = (Global.url+ "quests/" + quest_id + "/complete")
	var headers = ["Authorization: Bearer "+ Global.userToken]
	http_request.request(url,headers,HTTPClient.METHOD_POST)

func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main.tscn")
