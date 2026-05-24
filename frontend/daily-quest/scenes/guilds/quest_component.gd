extends Control

@export var quest_item_scene: PackedScene
@onready var quest_list = %QuestList

var quests: Array = []

func setup(p_quests: Array):
	quests = p_quests
	refresh()

func refresh():
	clear()
	for quest in quests:
		var ui = quest_item_scene.instantiate()
		quest_list.add_child(ui)
		ui.setup(quest)
		ui.quest_complete.connect(_on_quest_complete)

func clear():
	for child in quest_list.get_children():
		child.queue_free()

func _on_quest_complete(quest_id):
	get_parent().complete_quest(quest_id)
