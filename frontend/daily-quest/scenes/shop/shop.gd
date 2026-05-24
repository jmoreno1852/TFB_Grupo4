extends Node2D

@onready var http_request = $HTTPRequest
@onready var http_request_buy = $HTTPRequestBuy
@onready var popup = $AcceptDialog
@onready var grid : GridContainer = %GridContainer
@export var shop_item : PackedScene
var items_by_id := {}
var item_id : int = 0
var shop_data : Array = [
  {
	"item_id": "string",
	"name": "string",
	"description": "string",
	"type": "string",
	"equippable_slot": "string",
	"value": 0
  }
]

func _on_popup_confirmed():
	pass
func show_popup(title: String, message: String):
	popup.title = title
	popup.dialog_text = message
	popup.popup_centered()

func _ready() -> void:
	http_request.request_completed.connect(_http_request_completed)
	http_request_buy.request_completed.connect(_http_request_completed_buy)
	popup.confirmed.connect(_on_popup_confirmed)
	var error 
	var url = Global.url+"shop/items"
	var headers = ["Content-Type: application/json"]
	error = http_request.request(url, headers, HTTPClient.METHOD_GET)
	if error != OK:
		push_error("Error al enviar request: " + str(error))
	
func _http_request_completed(result, response_code, _headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	print("Código HTTP:", response_code)
	var response_text = body.get_string_from_utf8()
	var json = JSON.new()
	var parse_error = json.parse(response_text)

	if parse_error != OK:
		push_error("Error parseando JSON")
		print(response_text)
		return
	var response = json.get_data()
	print("Respuesta:", response)
	if response_code == 200:
		shop_data = response 
		setup_store()
	
func setup_store() -> void:
	print("SETTING UP STORE")
	print(shop_data)
	for data in shop_data:
		items_by_id[str(data["item_id"])] = data
		var temp = shop_item.instantiate()
		temp.item_buy_pressed.connect(on_item_buy_pressed)
		grid.add_child(temp)
		temp.custom_minimum_size = Vector2(250, 120)
		temp.visible = true
		temp.setup(data)
		print("Added:", temp)
	
func on_item_buy_pressed(item_id: String) -> void:
	var item = items_by_id[item_id]
	if Global.gold < item["value"]:
		show_popup("Not enough gold", "")
		return
		
	var url = Global.url+"shop/purchase"
	var _headers =  [
		"Content-Type: application/json",
		"Authorization: Bearer " + Global.userToken
	]
	var purchase = {
		"item_id": item_id,
		"quantity": 1
	}
	var json_body = JSON.stringify(purchase)
	var error = http_request_buy.request(
		url,
		_headers,
		HTTPClient.METHOD_POST,
		json_body
	)
	if error != OK:
		push_error("Error al enviar request: " + str(error))

func _http_request_completed_buy(result, response_code, _headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	print("Código HTTP:", response_code)
	var response_text = body.get_string_from_utf8()
	var json = JSON.new()
	var parse_error = json.parse(response_text)

	if parse_error != OK:
		push_error("Error parseando JSON")
		print(response_text)
		return
	var response = json.get_data()
	print("Respuesta:", response)
	if response_code == 200:
		show_popup("", "Purchased successfully")
	elif response_code == 409:
		show_popup("Not enough gold", response.get("detail", "Insufficient funds"))
	elif response_code == 422:
		var messages = []
		for err in response["detail"]:
			messages.append(err["msg"])
		show_popup("Validation error", "\n".join(messages))
	else:
		show_popup("Error", "Server error: " + str(response_code))
		
func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main.tscn")
