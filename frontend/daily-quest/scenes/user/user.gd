extends Node

@onready var http_request_inv = $HTTPRequestInv

var inventory: Array = []
var equipment: Dictionary = {
	"weapon": "",
	"helmet": "",
	"armor": "",
	"leg_armor": "",
	"boots": "",
	"accessory": ""
}

func load_inventory():
	var url = Global.url + "inventory/me"
	var headers = [
		"Authorization: Bearer " + Global.userToken
	]
	http_request_inv.request(url, headers, HTTPClient.METHOD_GET)

func _on_http_request_completed(result, response_code, headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	var json = JSON.new()
	if json.parse(body.get_string_from_utf8()) != OK:
		return 
	var response = json.get_data()
	if response.has("items"):
		inventory = response["items"]
	if response.has("equipment"):
		equipment = response["equipment"]
		
func _on_inventory_pressed():
	$InventoryComponent.visible = true
	$InventoryComponent.setup(inventory, equipment)

func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main.tscn")
