extends Control

var character_names = []
@onready var WhatIf = $WhatIf 
var WHAT_IF_PREFIX = "What if we shipped "
var WHAT_IF_POSTFIX = "%s and %s?"
var SWITCH_SPEED = 0.6
var SUSTAIN = 1.7
var recently_switched_names := false
var time = 0.0

# Called when the node enters the scene tree for the first time.
func _ready():
	randomize()
	var char_names_file = FileAccess.open("res://test/character_names_whatif.txt", FileAccess.READ)
	
	if char_names_file.is_open():
		var text = char_names_file.get_as_text()
		character_names = text.split('\n')
	# get a few random character names into Godot.
	print(character_names.size())
	pass

func get_two_random_names():
	var rand1 = randi() % character_names.size()
	var rand2 = randi() % character_names.size()
	return [character_names[rand1], character_names[rand2]]
	
# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):		
	var ratio = sin(time*SWITCH_SPEED) * sin(time*SWITCH_SPEED) * SUSTAIN
	WhatIf.visible_ratio = clamp(ratio, 0.0, 0.999999)
	print(WhatIf.visible_ratio)
	WhatIf.visible_characters = max(WhatIf.visible_characters, WHAT_IF_PREFIX.length())
	if ratio < 0.01 and not recently_switched_names:
		recently_switched_names = true
		WhatIf.text = WHAT_IF_PREFIX + (WHAT_IF_POSTFIX % get_two_random_names())
	if WhatIf.visible_ratio >= 0.9:
		recently_switched_names = false
		
	time += delta
	# randomize some names.
	pass


func _on_texture_button_pressed():	
	get_tree().change_scene_to_file("res://overview.tscn")
