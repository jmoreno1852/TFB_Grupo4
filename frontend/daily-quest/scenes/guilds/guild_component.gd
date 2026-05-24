extends PanelContainer

@export var guild_item_scene: PackedScene
@onready var guild_list = %GuildList

var guilds: Array = []
var current_guild_id := ""

func setup(p_guilds: Array, p_current_guild_id := ""):
	guilds = p_guilds
	current_guild_id = p_current_guild_id
	refresh()

func refresh():
	clear()
	for guild in guilds:
		var ui = guild_item_scene.instantiate()
		guild_list.add_child(ui)
		ui.setup(guild, current_guild_id)
		ui.guild_action.connect(_on_guild_action)

func clear():
	for child in guild_list.get_children():
		child.queue_free()

func _on_guild_action(guild_id, already_joined):
	if already_joined:
		get_parent().leave_guild(guild_id)
	else:
		get_parent().join_guild(guild_id)
