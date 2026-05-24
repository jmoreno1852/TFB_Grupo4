extends PanelContainer

signal guild_action(guild_id, already_joined)
var guild_data = {}
var is_joined := false

@onready var guild_name = %GuildName
@onready var guild_description = %GuildDescription
@onready var button = %GuildButton

func setup(data, current_guild_id: String):
	guild_data = data
	guild_name.text = data.get("name", "")
	guild_description.text = data.get("description", "")
	is_joined = data["id"] == current_guild_id
	if is_joined:
		button.text = "Leave"
	else:
		button.text = "Join"
	

func _on_join_button_pressed():
	guild_action.emit(
		guild_data["id"],
		is_joined
	)
