extends Control

signal item_buy_pressed(item_id)

var item_id : String

@onready var texture = $VBoxContainer/TextureRect
@onready var heading = $VBoxContainer/Label
@onready var desc = $VBoxContainer/Desc

func setup(data: Dictionary) -> void:
	#texture.texture = load(data.get(""))
	heading.text = data.get("name", "")
	desc.text = data.get("description", "")
	item_id = str(data.get("item_id", ""))

func _on_buy_pressed():
	item_buy_pressed.emit(item_id)
