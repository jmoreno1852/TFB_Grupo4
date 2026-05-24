extends Control

@export var inventory_item_scene: PackedScene
@onready var grid = $PanelContainer/MarginContainer/HSplitContainer/ScrollContainer/GridContainer
@onready var equip_button = %Equip
@onready var http_request = %HTTPRequest

var inventory: Array = []
var equipment: Dictionary = {}
var selected_item: Dictionary = {}

func setup(p_inventory: Array, p_equipment: Dictionary):
	inventory = p_inventory
	equipment = p_equipment
	
	%WeaponSlot.text = equipment.get("weapon", "Empty")
	%HelmetSlot.text = equipment.get("helmet", "Empty")
	%ArmorSlot.text = equipment.get("armor", "Empty")
	%BootsSlot.text = equipment.get("boots", "Empty")
	%AccessorySlot.text = equipment.get("accessory", "Empty")
	refresh()

func refresh():
	if grid == null:
		return
	clear_grid()
	for child in grid.get_children():
		child.queue_free()
	for item in inventory:
		var ui = inventory_item_scene.instantiate()
		grid.add_child(ui)
		ui.setup(item)
		ui.item_selected.connect(_on_item_selected)

func clear_grid():
	for child in grid.get_children():
		child.queue_free()

func _on_item_selected(item):
	selected_item = item
	print(item)


func _on_equip_pressed() -> void:
	if not selected_item.has("item_id"):
		return
	var url = Global.url + "inventory/equip"
	var headers = [
		"Authorization: Bearer " + Global.userToken,
		"Content-Type: application/json"
	]
	var body = JSON.stringify({
		"item_id": selected_item["item_id"]
	})
	http_request.request(
		url,
		headers,
		HTTPClient.METHOD_POST,
		body
	)

func _on_http_request_request_completed(result: int, response_code: int, headers: PackedStringArray, body: PackedByteArray) -> void:
	if result != HTTPRequest.RESULT_SUCCESS:
		return
	var json = JSON.new()
	if json.parse(body.get_string_from_utf8()) != OK:
		return
	var response = json.get_data()
	if response_code == 200:
		print("Equipped!")
		selected_item = {}
		refresh()
		get_parent().load_inventory()
	else:
		print(response)

func _on_back_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/main.tscn")
