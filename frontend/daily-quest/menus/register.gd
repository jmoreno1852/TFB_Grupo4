extends Control

@onready var http_request = $HTTPRequest
@onready var username = $VBoxContainer/username
@onready var password = $VBoxContainer/password
@onready var popup = $AcceptDialog
var popup_success: bool = false

func _ready():
	http_request.request_completed.connect(_http_request_completed)
	popup.confirmed.connect(_on_popup_confirmed)
	
func _on_exit_pressed():
	get_tree().change_scene_to_file("res://menus/menu.tscn")
	
func show_popup(title: String, message: String, success: bool=false):
	popup_success = success
	popup.title = title
	popup.dialog_text = message
	popup.popup_centered()
	
func _on_register_pressed():
	if username.text.is_empty():
		show_popup("","Email cannot be empty")
		return
	if not username.text.contains("@"):
		show_popup("","Invalid email")
		return
	if password.text.length() < 8:
		show_popup("","Password must have at least 8 characters")
		return
	var error 
	var url = Global.url+"auth/register"
	var headers = ["Content-Type: application/json"]
	var query = {"email": username.text,"password": password.text}
	error = http_request.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(query))
	if error != OK:
		push_error("Error al enviar request: " + str(error))

func _http_request_completed(result, response_code, headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		show_popup("","Connection error")
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
	match response_code:
		201:
			show_popup("Registered successfully","Your account has been created.",true)
		409:
			show_popup("","Email already exists.")
		422:
			var messages = []
			for err in response["detail"]:
				messages.append(err["msg"])
			show_popup("Validation error","\n".join(messages))
		_:
			show_popup("","Server error: "+ str(response_code))

func _on_popup_confirmed():
	if popup_success:
		get_tree().change_scene_to_file("res://menus/login.tscn")
