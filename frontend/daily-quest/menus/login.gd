extends Control

@onready var http_request = $HTTPRequest
@onready var username = $VBoxContainer/username
@onready var password = $VBoxContainer/password
@onready var popup = $AcceptDialog
var popup_success: bool = false

func _ready():
	http_request.request_completed.connect(_on_http_request_completed)
	popup.confirmed.connect(_on_popup_confirmed)
	
func _on_exit_pressed():
	get_tree().change_scene_to_file("res://menus/menu.tscn")

func show_popup(title: String, message: String, success: bool=false):
	popup_success = success
	popup.title = title
	popup.dialog_text = message
	popup.popup_centered()
	
func _on_login_pressed():
	if username.text.is_empty():
		show_popup("","Email cannot be empty")
		return
	if not username.text.contains("@"):
		show_popup("","Invalid email")
		return
	if password.text.length() < 8:
		show_popup("","Password must have at least 8 characters")
		return

	var url = Global.url + "auth/login" 
	var headers = ["Content-Type: application/json"]
	var credentials = {
		"email": username.text,
		"password": password.text
	}
	var error = http_request.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(credentials))
	if error != OK:
		push_error("Error sending request: " + str(error))

func _on_http_request_completed(result, response_code, _headers, body):
	if result != HTTPRequest.RESULT_SUCCESS:
		show_popup("","Connection error")
		return

	var response_text = body.get_string_from_utf8()
	var json = JSON.new()
	var parse_error = json.parse(response_text)
	if parse_error != OK:
		show_popup("","Invalid server response")
		return

	var response = json.get_data()
	match response_code:
		200:
			Global.userToken = response["access_token"]
			Progression.load_progression()
			show_popup("", "Loged in succesfully.", true)
		401:
			show_popup("","Invalid credentials")
		422:
			# Validation errors
			var messages = []
			for err in response["detail"]:
				messages.append(err["msg"])
			show_popup("","\n".join(messages))
		_:
			show_popup("","Server error: " + str(response_code))

func _on_popup_confirmed():
	if popup_success:
		get_tree().change_scene_to_file("res://scenes/main.tscn")
