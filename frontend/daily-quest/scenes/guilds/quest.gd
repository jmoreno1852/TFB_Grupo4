extends Control

signal quest_complete(quest_id)
var quest_data = {}

@onready var title_label = %Title
@onready var description = %Description
@onready var rewards = %Rewards
@onready var complete_button = %CompleteButton

func setup(data):
	quest_data = data
	title_label.text = data.get("title","")
	description.text = data.get("description","")
	rewards.text = (
		"XP %d | Gold %d"
		% [data.get("xp_reward",0),data.get("gold_reward",0)]
	)
	var status = data.get("status","active")
	complete_button.disabled = (status == "completed")
	if status == "completed":
		complete_button.text = "Completed"

func _on_complete_button_pressed():
	quest_complete.emit(quest_data["id"])
