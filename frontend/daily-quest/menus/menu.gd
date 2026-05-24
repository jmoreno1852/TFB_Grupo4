extends Control

func _on_login_pressed() -> void:
	get_tree().change_scene_to_file("res://menus/login.tscn")

func _on_signin_pressed() -> void:
	get_tree().change_scene_to_file("res://menus/signin.tscn")

func _on_exit_pressed() -> void:
	get_tree().quit()
