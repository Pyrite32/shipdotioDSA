extends Control

var unpack_binary_thread: Thread
var sort_thread : Thread


var is_searchable = false
var modifying_data = false

var left_bar_result = false
var right_bar_result = false

var global_should_stop_sorting = false


var length_of_longest_str = 0
var characters_dataset = []
var characters_dataset_shadow = []
var characters_dataset_sorted = []
var dataset_size = 0


@onready var ENABLED_SEARCH_BAR = preload("res://textures/search-bar.png")
@onready var DISABLED_SEARCH_BAR = preload("res://textures/search-bar-disabled.png")
@onready var ENABLED_HEART = preload("res://textures/heart-button.png")
@onready var DISABLED_HEART = preload("res://textures/heart-button-disabled.png")
@onready var DEFAULT_PFP = preload("res://textures/placeholder-photo.png")

@onready var LEFT_SEARCH_BAR_TEXTURE = $SearchBars/HBoxContainer/SearchBarLeftTexture
@onready var RIGHT_SEARCH_BAR_TEXTURE = $SearchBars/HBoxContainer/SearchBarRightTexture
@onready var HEART_BUTTON = $HeartButton/HeartButtonTexture
@onready var LEFT_SEARCH_BAR_LINE = $SearchBars/HBoxContainer/SearchBarLeftTexture/LineEditLeft
@onready var RIGHT_SEARCH_BAR_LINE = $SearchBars/HBoxContainer/SearchBarRightTexture/LineEditRight

@onready var CHIP_TEXTURE = $StatusBar/StatusBarChip
@onready var STATUS_BAR_TEXTURE = $StatusBar/StatusBarTexture
@onready var STATUS_BAR_LABEL = $StatusBar/LoadMessage

@onready var CHIP_BUSY = preload("res://textures/status-loading-chip.png")
@onready var CHIP_READY = preload("res://textures/status-ready-chip.png")

@onready var SEARCH_ELEMENT_SCENE = preload("res://search_element.tscn")
@onready var SEARCH_ELEMENT_NO_RESULTS_SCENE = preload("res://search_element_no_results.tscn")

var left_char_temp_texture : Texture
var right_char_temp_texture : Texture
var temp_texture : Texture

# Called when the node enters the scene tree for the first time.
func _ready():
	# check if unpacked_tensors exists.
	randomize()
	$Verdict.hide()
	$VerdictRemarks.hide()
	
	var unpacked_file_location = "res://data/unpacked.csv"
	if FileAccess.file_exists(unpacked_file_location):
		unpack_binary_thread = Thread.new()
		modifying_data = true
		unpack_binary_thread.start(import_csv)
		
	else:
		update_status_text("dataset not found!")
	pass
	
	
	# try to run the unpacking task if no unpacked tensors have been detected.
	# run task on thread
	# read file every half second with progress in it
	# display progress.
	
	# if unpacked:
	# copy over to this characters_dataset
	# apply annealing
	
	# condition: waiting to apply sort = true.
	pass
	
func set_status_ready(additional=''):
	STATUS_BAR_LABEL.text = "READY" + additional
	CHIP_TEXTURE.texture = CHIP_READY
	STATUS_BAR_TEXTURE.material.set_shader_parameter("enabled", false)
	enable_all()
	
func set_status_busy():
	CHIP_TEXTURE.texture = CHIP_BUSY
	STATUS_BAR_TEXTURE.material.set_shader_parameter("enabled", true)
	disable_all()
	
func enable_all():
	HEART_BUTTON.texture_normal = ENABLED_HEART
	LEFT_SEARCH_BAR_TEXTURE.texture = ENABLED_SEARCH_BAR
	RIGHT_SEARCH_BAR_TEXTURE.texture = ENABLED_SEARCH_BAR
	LEFT_SEARCH_BAR_LINE.editable = true
	is_searchable = true
	
func disable_all():
	HEART_BUTTON.texture_normal = DISABLED_HEART
	LEFT_SEARCH_BAR_TEXTURE.texture = DISABLED_SEARCH_BAR
	RIGHT_SEARCH_BAR_TEXTURE.texture = DISABLED_SEARCH_BAR
	LEFT_SEARCH_BAR_LINE.editable = false
	is_searchable = false

func update_status_text(text):
	STATUS_BAR_LABEL.text = text
	
func clear_left_search_bar_entries():
	var children = LEFT_SEARCH_BAR_TEXTURE.get_node("VBoxContainer").get_children()
	for child in children:
		child.queue_free()
		
func clear_right_search_bar_entries():
	var children = RIGHT_SEARCH_BAR_TEXTURE.get_node("VBoxContainer").get_children()
	for child in children:
		child.queue_free()
		
func update_search_bar(search_bar:LineEdit, max=4):
	var is_left = false
	if search_bar.name == "LineEditLeft":
		is_left = true
		clear_left_search_bar_entries()
	else:
		clear_right_search_bar_entries()
	var text = search_bar.text
	var matches = bin_search_all_that_matches(text)
	var result = []
	for i in range(0, min(matches.size(),max)):
		
		result.append(matches[i])
	if result.size() > 0:
		for res in result:
			spawn_new_search_term(res, search_bar.get_parent(), is_left)
		if is_left:
			left_bar_result = true
		else:
			right_bar_result = true
	else:
		if is_left:
			left_bar_result = false
		else:
			right_bar_result = false
		spawn_no_results_term(search_bar.get_parent())
	return result
	
func spawn_no_results_term(search_bar:TextureRect):
	var image_search_no_result = SEARCH_ELEMENT_NO_RESULTS_SCENE.instantiate()
	search_bar.get_node("VBoxContainer").add_child(image_search_no_result)
	pass
	
func spawn_new_search_term(character_name:String, search_bar:TextureRect, is_left):
	var image_search = SEARCH_ELEMENT_SCENE.instantiate()
	search_bar.get_node("VBoxContainer").add_child(image_search)
	var image_file_path = ProjectSettings.globalize_path(".//profile-pictures/"+character_name+".png")
	if FileAccess.file_exists(image_file_path):
		var image = Image.new()
		image.load_png_from_buffer(FileAccess.get_file_as_bytes(image_file_path))
		var average_r = 0.0
		var average_g = 0.0
		var average_b = 0.0
		var total_pixels = image.get_width() * image.get_height()
		for y in range(0, image.get_height()):
			for x in range(0, image.get_width()):
				var color = image.get_pixel(x,y)
				average_r += color.r
				average_g += color.g
				average_b += color.b
		var final_color = Color( average_r / total_pixels,
								 average_g / total_pixels,
								 average_b / total_pixels)
		temp_texture = ImageTexture.new()
		temp_texture = ImageTexture.create_from_image(image)
		image_search.get_node("PFP").texture = temp_texture
		image_search.get_node("Gradient").modulate = final_color
		
		if is_left:
			left_char_temp_texture = temp_texture
		else:
			right_char_temp_texture = temp_texture
		
	else:
		if is_left:
			left_char_temp_texture = DEFAULT_PFP
		else:
			right_char_temp_texture = DEFAULT_PFP
		
	var names = character_name.split("_")
	if names.size() == 2:
		image_search.get_node("Name").text = names[0]
		image_search.get_node("ShowName").text = names[1]
	else:
		image_search.get_node("Name").text = character_name
	pass
	
func bin_search_all_that_matches(text:String, max_matches=100):
	text = text.to_lower()
	if (text.length() >= 2):
		print(characters_dataset_sorted.size())
		var idx = binary_search_with_substring(characters_dataset_sorted, text)
		if (idx == -1):
			return []
		var first_range_idx = idx
		var last_range_idx = idx
		var reduced_search_string = characters_dataset[idx][0].substr(0,text.length())
		while characters_dataset[first_range_idx][0] <= reduced_search_string and first_range_idx > 0:
			first_range_idx -= 1
		while characters_dataset[last_range_idx][0] >= reduced_search_string and last_range_idx < dataset_size:
			last_range_idx += 1
		var result = []
		var counter = 0
		for i in range(first_range_idx,last_range_idx):
			result.append(characters_dataset[i][0])
			if counter >= max_matches:
				break
		return result
	return []
			
func binary_search_with_substring(arr: Array, x: String):
	var low = 0
	x = x.to_lower()
	var high = arr.size() - 1

	while low <= high:
		var mid = int(int(low + high) / 2)
		var mid_word : String = arr[mid].to_lower()

		# Check if the search string is a substring of the mid_word
		if mid_word.begins_with(x):
			return mid

		if x < mid_word:
			high = mid - 1
		else: # Otherwise, search in the right half of the array
			low = mid + 1

	return -1
	
func binary_search_exact(arr: Array, x: String):
	var low = 0
	var high = arr.size() - 1

	while low <= high:
		var mid = int(int(low + high) / 2)
		var mid_word : String = arr[mid]

		# Check if the search string is a substring of the mid_word
		if mid_word == x:
			return mid

		# If the search string is lexicographically less than the mid_word,
		# search in the left half of the array
		if x < mid_word:
			high = mid - 1
		else: # Otherwise, search in the right half of the array
			low = mid + 1

	return -1

func get_lsd_char_at(string, index):
	if index < string.length():
		return int(string[index]) % 256
	else:
		return 0
		
func lsd_radix_sort(array):
	var array_size = array.size()
	var meta_max_progress = length_of_longest_str - 1
	var internal_progress_max = 5
	var meta_progress = 0
	var internal_progress = 0
	for i in range(length_of_longest_str - 1, -1, -1):
		if global_should_stop_sorting:
			break
		internal_progress = 0
		var count = []
		var out_arr = []
		for num in range(256):
			count.append(0)
		
		internal_progress += 1
		update_status_text("LSD Radix Sort %s of %s : [%s/%s]" %
		 [meta_progress, meta_max_progress, internal_progress, internal_progress_max])
		
		for word in array:
			var index = get_lsd_char_at(word, i)
			count[index] += 1
			
		internal_progress += 1
		update_status_text("LSD Radix Sort %s of %s : [%s/%s]" %
		 [meta_progress, meta_max_progress, internal_progress, internal_progress_max])
		
		for num in range(1,256):
			count[num] += count[num-1]
			
		internal_progress += 1
		update_status_text("LSD Radix Sort %s of %s : [%s/%s]" % 
		[meta_progress, meta_max_progress, internal_progress, internal_progress_max])
			
		for j in range(array_size - 1, 0, -1):
			var index = get_lsd_char_at(array[j], i)
			var uindex = clamp(count[index]-1, 0,out_arr.size()-1 )
			if uindex == -1:
				uindex = 0
			else:
				out_arr[uindex] = array[j]
			count[index] -= 1
			
		internal_progress += 1
		update_status_text("LSD Radix Sort %s of %s : [%s/%s]" % 
		[meta_progress, meta_max_progress, internal_progress, internal_progress_max])
			
		for num in range(array_size):
			if out_arr.size() < 1:
				break
			array[num] = out_arr[num]
		
		internal_progress += 1
		update_status_text("LSD Radix Sort %s of %s : [%s/%s]" % 
		[meta_progress, meta_max_progress, internal_progress, internal_progress_max])
		meta_progress += 1
	if global_should_stop_sorting:
		global_should_stop_sorting = false
		$SortStopwatch.stop()
		return false
	set_status_ready("... Sort Time: %ss" % str($SortStopwatch.wait_time - $SortStopwatch.time_left))
	$SortStopwatch.stop()
	return true
	
func cocktail_shaker_sort(array:Array):
	var min = 0
	var max = array.size() - 1
	var max_progress = max + 1
	var progress = 0
	var should_continue = true
	while should_continue:
		if global_should_stop_sorting:
			break
		should_continue = false
		for i in range(min,max):
			if array[i] > array[i+1]:
				var temp = array[i]
				array[i] = array[i+1]
				array[i+1] = temp
				should_continue = true
		progress = min(progress+1,max_progress)
		update_status_text("Cocktail Sort... [%s/%s]" % [progress, max_progress])
		if not should_continue: # sort over
			break
		should_continue = false
		max -= 1
		for i in range(max, min, -1):
			if array[i] < array[i-1]:
				var temp = array[i]
				array[i] = array[i-1]
				array[i-1] = temp
				should_continue = true
		progress = min(progress+1,max_progress)
		update_status_text("Cocktail Sort... [%s/%s]" % [progress, max_progress])
		min += 1
	if global_should_stop_sorting:
		global_should_stop_sorting = false
		$SortStopwatch.stop()
		return false
	set_status_ready("... Sort Time: %ss" % str($SortStopwatch.wait_time - $SortStopwatch.time_left))
	$SortStopwatch.stop()
	return true
	pass
	
func import_csv():
	set_status_busy()
	print("hello from thread")
	var unpacked_file = FileAccess.open("res://data/unpacked.csv", FileAccess.READ)
	var data_size = int(FileAccess.open("res://data/size.txt", FileAccess.READ).get_as_text())
	var count = 0
	while not unpacked_file.eof_reached():
		var line = unpacked_file.get_csv_line()
		characters_dataset.append(line)
		length_of_longest_str = max(length_of_longest_str, line[0].length())
		characters_dataset_shadow.append(line[0])
		characters_dataset_sorted.append(line[0])
		update_status_text("Loading... %s/%s" % [count, 50536])
		count += 1
	var csv_data_offset_skip = 620
	var csv_data_offset_skip_progress = 0
	while count <= 50536:
		csv_data_offset_skip_progress += 1
		if csv_data_offset_skip_progress % csv_data_offset_skip == 0:
			characters_dataset_shadow.append(characters_dataset_sorted[randi() % characters_dataset.size()])
			count += 1
			update_status_text("Loading... %s/%s" % [count, 50536])
	dataset_size = data_size
	randomize_data()
	modifying_data = false
	print("longest: ",length_of_longest_str)

func randomize_data():
	set_status_busy()
	update_status_text("Randomizing...")
	$RandomTimer.start()
	await $RandomTimer.timeout
	characters_dataset_shadow.shuffle()
	update_status_text("Sort data to enable search")
	print("finish randomizing")
	prepare_lexical_data_for_sorting()
	
func compare_two_characters(char1, char2):
	# both characters are valid.
	var dot_product_sum = 0
	var char1_index = binary_search_exact(characters_dataset_sorted, char1)
	var char2_index = binary_search_exact(characters_dataset_sorted, char2)
	var char_1_vector = characters_dataset[char1_index].slice(1)
	var char_2_vector = characters_dataset[char2_index].slice(1)
	char_1_vector = normalized_vector(char_1_vector)
	char_2_vector = normalized_vector(char_2_vector)
	for i in range(0,min(char_1_vector.size(), char_2_vector.size())):
		dot_product_sum += char_1_vector[i] * char_2_vector[i]
	display_results(abs(dot_product_sum * 100.0))
	pass
	
func display_results(percent):
	$Verdict.show()
	$VerdictRemarks.show()
	if percent >= 90:
		set_verdict_remarks("Perfect match!")
	elif percent >= 75:
		set_verdict_remarks("Highly compatible")
	elif percent >= 60:
		set_verdict_remarks("Fairly decent")
	elif percent >= 30:
		set_verdict_remarks("Hmm...")
	elif percent >= 10:
		set_verdict_remarks("Not really...")
	else:
		set_verdict_remarks("Absolutely not")
	$Verdict.text = str(round(percent)) + "%"
	if percent >= 50:
		$Verdict.modulate = lerp(Color.YELLOW, Color.GREEN, (percent-0.5)*2.0 )
	else:
		$Verdict.modulate = lerp(Color.RED, Color.YELLOW, (percent)*2.0)
	
	pass
	
func set_verdict_remarks(text:String):
	$VerdictRemarks.text = text	

func sort_using_msd():
	var path_to_python = ProjectSettings.globalize_path("run-sort/pythonlocal.exe")
	if FileAccess.file_exists(path_to_python):
		var result = OS.execute(path_to_python, ["msd.py"])	
	pass
	
func sort_using_lsd():
	var path_to_python = ProjectSettings.globalize_path("run-sort/pythonlocal.exe")
	if FileAccess.file_exists(path_to_python):
		var result = OS.execute(path_to_python, ["lsd.py"])	
	pass

func _on_randomize_button_pressed():
	if not modifying_data:
		print("Randomize Button")
		modifying_data = true
		unpack_binary_thread = Thread.new()
		unpack_binary_thread.start(randomize_data)
	modifying_data = false

func prepare_lexical_data_for_sorting():
	var lexical_path = ProjectSettings.globalize_path("run-sort/lexical-data-rand.txt")
	if FileAccess.file_exists(lexical_path):
		var file = FileAccess.open(lexical_path, FileAccess.WRITE)
		for entry in characters_dataset_shadow:
			file.store_string(entry+"\n")

func _on_radix_msd_button_pressed():
	if not modifying_data:
		set_status_busy()
		update_status_text("Sorting...")
		modifying_data = true
		$SortStopwatch.start()
		sort_thread = Thread.new()
		sort_thread.start(cocktail_shaker_sort.bind(characters_dataset_shadow))
		
	#	disable_all()
	#	update_status_text("Sorting...")
	#	$SortStopwatch.start()
	#	await sort_using_msd()
	#	enable_all()
	#	set_status_ready("... Sort Time: %ss" % str(round($SortStopwatch.wait_time - $SortStopwatch.time_left)))
	#	$SortStopwatch.stop()
	#	modifying_data = false

func _on_radix_lsd_button_pressed():
	if not modifying_data:
		set_status_busy()
		update_status_text("Sorting...")
		modifying_data = true
		$SortStopwatch.start()
		sort_thread = Thread.new()
		sort_thread.start(lsd_radix_sort.bind(characters_dataset_shadow))
		
func exists(character_name):
	var idx = binary_search_exact(characters_dataset_sorted, character_name)
	return idx != -1
	
func normalized_vector(vector):
	var mag = magnitude_of_vector(vector)
	var result = []
	for dimension in vector:
		result.append(float(dimension) / mag)
	return result

func magnitude_of_vector(vector):
	var sum = 0
	for dimension in vector:
		sum += (float(dimension) * float(dimension))
	return sqrt(sum)

func lexical_compare_two_entries(en1, en2):
	print(en1[0])
	print(en2[0])
	if en1[0] > en2[0]:
		return 1
	elif en1[0] < en2[0]:
		return -1
	else:
		return 0

func _on_left_line_focus_entered():
	update_search_bar(LEFT_SEARCH_BAR_LINE)
	pass # Replace with function body.

func _on_right_line_focus_entered():
	update_search_bar(RIGHT_SEARCH_BAR_LINE)

func _on_line_edit_left_focus_exited():
	$MatchPFP1.show()
	var vbox_elements = LEFT_SEARCH_BAR_TEXTURE.get_node("VBoxContainer").get_children()
	if vbox_elements.size() > 0 and left_bar_result:
		var char_name = vbox_elements[0].get_node("Name").text
		var char_show = vbox_elements[0].get_node("ShowName").text
		LEFT_SEARCH_BAR_LINE.text = "%s_%s" % [char_name, char_show]
		$MatchPFP1.texture = vbox_elements[0].get_node("PFP").texture
	clear_left_search_bar_entries()
	
func _on_line_edit_right_focus_exited():
	$MatchPFP2.show()
	var vbox_elements = RIGHT_SEARCH_BAR_TEXTURE.get_node("VBoxContainer").get_children()
	if vbox_elements.size() > 0 and right_bar_result:
		var char_name = vbox_elements[0].get_node("Name").text
		var char_show = vbox_elements[0].get_node("ShowName").text
		RIGHT_SEARCH_BAR_LINE.text = "%s_%s" % [char_name, char_show]
		$MatchPFP2.texture = vbox_elements[0].get_node("PFP").texture
	clear_right_search_bar_entries()
		
func _on_line_edit_left_text_changed(new_text):
	update_search_bar(LEFT_SEARCH_BAR_LINE)

func _on_line_edit_right_text_changed(new_text):
	update_search_bar(RIGHT_SEARCH_BAR_LINE)



func _on_heart_button_texture_pressed():
	if not is_searchable:
		print("not searchable")
		return
	if LEFT_SEARCH_BAR_LINE.text == '':
		print("no text in left")
		return
	if RIGHT_SEARCH_BAR_LINE.text == '':
		print("no text in right")
		return
	if not exists(LEFT_SEARCH_BAR_LINE.text):
		print(LEFT_SEARCH_BAR_LINE.text," not exists")
		return
	if not exists(RIGHT_SEARCH_BAR_LINE.text):
		print(RIGHT_SEARCH_BAR_LINE.text," not exists")
		return
	print("ok")
	compare_two_characters(LEFT_SEARCH_BAR_LINE.text, RIGHT_SEARCH_BAR_LINE.text)
	pass # Replace with function body.


func _on_line_edit_left_mouse_exited():
	_on_line_edit_left_focus_exited()


func _on_line_edit_right_mouse_exited():
	_on_line_edit_right_focus_exited()


func _on_heart_button_texture_button_down():
	print("HEART DOWN")


func _on_radix_lsd_button_2_pressed():
	if not is_searchable and modifying_data:
		global_should_stop_sorting = true
		set_status_busy()
		update_status_text("Aborted...")
		modifying_data = false
