extends Node2D

@onready var http_request_prog = $HTTPRequestProg
@onready var lvl_label = %lvl
@onready var exp_label = %exp
@onready var gold_label = %gold

func _ready():
	lvl_label.text = "LVL: " + str(Global.level)
	exp_label.text = "XP: " + str(Global.xp)
	gold_label.text = "Gold: " + str(Global.gold)
	
func _on_shop_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/shop/shop.tscn")

func _on_quests_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/guilds/quests.tscn")

func _on_guild_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/guilds/guilds.tscn")

func _on_home_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/guilds/quests.tscn")

func _on_config_pressed() -> void:
	get_tree().change_scene_to_file("res://scenes/user/user.tscn")
