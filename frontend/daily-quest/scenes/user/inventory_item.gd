extends Button

signal item_selected(item)

var item: Dictionary = {}

@onready var name_label = %NameLabel
@onready var quantity_label = %QuantityLabel

func setup(item_data: Dictionary):
	item = item_data
	name_label.text = item.get("item_id", "")
	quantity_label.text = "x%d" % item.get("quantity", 0)

func _pressed():
	item_selected.emit(item)
