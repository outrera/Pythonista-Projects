import ui,sqlite3,datetime,sound,console,clipboard,dialogs


# This script uses 2 tables from the database, but there are others for translations
"""
table_name: t_kjv
	records:
		b - book (int)
		c - chapter (int)
		v - verse (int)
		t - text (str)

table_name: key_english
	records:
		b - book (int)
		n - name (str)

table_name: bible_version_key
		id
		table
		abbreviation
	
American Standard - ASV1901 (ASV)
Bible in Basic English - (BBE)
Darby
King James Version (KJV)
Webster's Bible (WBT)
World English Bible (WEB)
Young's Literal Translation (YLT)
"""

database = 'bible-sqlite.db'
# I'd like to add a timestamp to notes, so:
time_stamp = datetime.datetime.today().strftime('%m_%d_%Y_%H:%M:%S')
# File name for our notes file (here for easy access)
save_file = 'notes.txt'
# File name for our thoughts file.
thoughts_file = 'thoughts.txt'

# We will load the following list into a list dialog
translations=["American Standard - ASV1901 (ASV)",
"Bible in Basic English - (BBE)",
"Darby - (DBY)",
"King James Version (KJV)",
"Webster's Bible (WBT)",
"World English Bible (WEB)",
"Young's Literal Translation (YLT)"]

# If you change a .pyui file to .json you can load that JSON as a string from your code.
# Good way to be unnecessarily cryptic. Also good for simple views.
welcome_screen="""
[
  {
    "class" : "View",
    "attributes" : {
      "background_color" : "RGBA(1.000000,1.000000,1.000000,1.000000)",
      "tint_color" : "RGBA(0.000000,0.478000,1.000000,1.000000)",
      "enabled" : true,
      "border_color" : "RGBA(0.000000,0.000000,0.000000,1.000000)",
      "flex" : ""
    },
    "frame" : "{{0, 0}, {455, 112}}",
    "selected" : false,
    "nodes" : [
      {
        "class" : "Label",
        "attributes" : {
          "font_size" : 44,
          "text" : "WELCOME",
          "font_name" : "Avenir-Light",
          "name" : "label1",
          "text_color" : "RGBA(0.877358,0.877358,0.356427,1.000000)",
          "class" : "Label",
          "alignment" : "center",
          "frame" : "{{153, 40}, {150, 32}}",
          "uuid" : "DD90573A-00EF-48E3-9294-6EFD83AFE325"
        },
        "frame" : "{{85, 11}, {296, 45}}",
        "selected" : false,
        "nodes" : [

        ]
      },
      {
        "class" : "Label",
        "attributes" : {
          "font_size" : 18,
          "text" : "Tutorial Doctor",
          "font_name" : "<System>",
          "name" : "label2",
          "text_color" : "RGBA(0.783019,0.783019,0.220224,1.000000)",
          "class" : "Label",
          "alignment" : "center",
          "frame" : "{{153, 40}, {150, 32}}",
          "uuid" : "3F07C608-DDFC-4C9D-9B34-790AC7DD4DF6"
        },
        "frame" : "{{138, 64}, {202, 32}}",
        "selected" : false,
        "nodes" : [

        ]
      }
    ]
  }
]
"""

# A quick intro view demonstrating animation. Fades-out
def intro():
	v=ui.load_view_str(welcome_screen)
	v.background_color='white'
	v.present('sheet',hide_title_bar=True)
	def exit():
		v.close()
	def fade():
		v.alpha=0
	ui.animate(fade,.5,1,exit)

# closes the superview of the sender
def close(sender):
	sender.superview.close()

# save text in a view to the clipboard
def clip(sender):
	clipboard.set(thoughts.text)
	console.alert('Saved to Clipboard')

# open a list dialog
def translate(sender):
	show=dialogs.list_dialog('Translations',translations)
	print(show)

# open the IOS share sheet
def share(sender):
	dialogs.share_text(thoughts.text)

# load sqlite3 query into a tableview as a result of a segmented control action
def test(sender):
	con = sqlite3.connect(database)
	cursor=con.cursor()
	# A query to get all old testament book names in the 'key_english' table 
	ot_query = 'select n from key_english where b < 40'
	ot_bks = [x[0] for x in cursor.execute(ot_query)]
	
	# A query to get all new testament book names in the 'key_english' table 
	nt_query = 'select n from key_english where b >= 40'
	nt_bks = [x[0] for x in cursor.execute(nt_query)]
	
	selected_testament = sender.segments[sender.selected_index]
	
	if selected_testament=='Old Testament':
		books.data_source.items=ot_bks
	
	elif selected_testament=='New Testament':
		books.data_source.items= nt_bks

# Updates the table and text views
def updates(*args):
	# Connect to the sqlite database and create a cursor to query it with
	con = sqlite3.connect(database)
	cursor=con.cursor()
	# Three argument parameters (all tanleviews) that were passed in using a lambda function.
	tbl_books = args[0]
	tbl_chapters = args[1]
	control_testaments = args[2]
	
	# A query to get all book names in the 'key_english' table
	all_bks_query = 'select n from key_english'
	all_bks = [x[0] for x in cursor.execute(all_bks_query)]
	
	# Store tableview selections
	selected_book = tbl_books.items[tbl_books.selected_row]
	selected_chap = tbl_chapters.items[tbl_chapters.selected_row]
	#selected_testament = control_testaments.segments[control_testaments.selected_index]
	
	
	# Select book from the key_english table where the name = the selected book/cell of a tableview
	num_query = "select b from key_english where n='{}'".format(selected_book)
	bk_num=[x for x in cursor.execute(num_query)][0][0]
	
	c = selected_chap # unnecessary perhaps but using 'c' is shorter.
	
	# Select chapter,verse,text from the t_kjv table where book = book number (tableview) and chapter = selected chapter
	txt_query = "select c,v,t from 't_kjv' where b = '{}' AND c = '{}'".format(bk_num,c)
	txt = [row for row in cursor.execute(txt_query)]
	# Format the text as -- ''+chapter+text -- ('' can be replaced with whatever prefix you want)
	txt_formatted = "\n".join("{} {}: {}\n".format('',c,t) for b,c,t in txt)
	
	# If the formatted text is an empty string, set the contents textview to a string
	# This is a quick fix if a user selects a chapter in a book that doesn't exist for that book
	if txt_formatted=='':
		contents.text = 'Chapter does not exist'
	
	# Otherwise, set the contents textview to the formatted text
	else: contents.text = txt_formatted
	# Set the heading label to the selected book plus the selected chapter (as a string)
	heading.text=selected_book+' '+str(selected_chap)

#	Save text/selected text in a textview to a file
def save_selection(sender):
	'''saves text/selected text in a textview to a file. If no text is selected, the entire text is saved.'''
	# Get the beginning of the textview selection
	beg= contents.selected_range[0]
	# Get the end of the textview selection
	end = contents.selected_range[1]
	# Get the entire text in the textview
	txt = contents.text
	# If text is selected (if there is a substring from beginning to end)...
	with open(save_file,'a') as outfile:
		if txt[beg:end] != '':
			# write the text to a file with a timestamp, the heading lable text, and the selected text.
			outfile.write('\n'+time_stamp+'\n'+heading.text+'\n\n'+txt[beg:end]+'\n')
		# Otherwise...
		else:
			# write the entire text to the file.
			outfile.write('\n'+time_stamp+'\n'+heading.text+'\n\n'+txt+'\n')
	# Play a sound
	sound.play_effect('ui:switch8')
	# Alert the user that fhe file has been saved to the file.
	console.alert('Saved to {}'.format(save_file))

# Same logic as save_selection
def selectionToThoughts(sender):
	beg= contents.selected_range[0]
	end = contents.selected_range[1]
	txt = contents.text
	if txt[beg:end] != '':
		thoughts.text = thoughts.text +heading.text+'\n'+txt[beg:end]+'\n\n'
	else:
		thoughts.text = thoughts.text +heading.text+'\n'+txt+'\n\n'
	sound.play_effect('rpg:DrawKnife2')

# Save text of a textview to a file
def save_thoughts(sender):
	with open(thoughts_file,'a')	as outfile:
		outfile.write(time_stamp+'\n'+thoughts.text+'\n')
	sound.play_effect('rpg:BookFlip2')
	console.alert('Saved to {}'.format(thoughts_file))

# Make a textview editable or not editable with a switch.
def freeze(sender):
	if sender.value == True:
		thoughts.editable=True
	if sender.value==False:
		thoughts.editable=False

# Load text from a file into the 'thoughts' textview
def load_thoughts(sender):
	with open(thoughts_file,'r') as infile:
		thoughts.text = infile.read()

# Set the 'thoughts' textview to an empty string (clear it).
def clear_thoughts(sender):
	thoughts.text=''

# Creating a quick popup sheet to preview a text file called 'thoughts.txt' (see top)
def view_thoughts(sender):
	v=ui.View()
	v.width=540
	v.height=540
	v.background_color='white'
	tv=ui.TextView()
	tv.width=v.width
	tv.height=v.height
	tv.background_color=''
	tv.editable=False
	tv.font=('Times New Roman',18)
	with open(thoughts_file,'r') as infile:
		tv.text=infile.read()
	v.add_subview(tv)
	v.present('sheet')
# I think it is okay to use single-letter variable names for small tasks, but certainly not all throughout your code. Comments help here also.

# IMPLEMENTATION
# Getting ui elements and setting actions
bible = ui.load_view()
heading = bible['book_heading']
books = bible['books']
chapters = bible['chapters']
contents = bible['contents']
testaments = bible['testaments']
testaments2 = bible['testaments2']
testaments2.action=test
thoughts = bible['view1']['thought_bubble']
thoughts_switch = bible['view1']['switch']
thoughts_switch.action = freeze
thoughts_button = bible['view1']['btn_thoughts']
thoughts_button.action = selectionToThoughts
thoughts_save_button = bible['view1']['btn_save_thoughts']
thoughts_save_button.action = save_thoughts
load_button = bible['view1']['btn_load']
load_button.action = load_thoughts
clear_button = bible['view1']['btn_clear']
clear_button.action=clear_thoughts
save_button = bible['view1']['btn_save']
save_button.action=save_selection
close_button = bible['btn_close']
close_button.action=close
clip_button = bible['view1']['btn_clip']
clip_button.action=clip
translate_button = bible['view1']['btn_translate']
translate_button.action=translate
share_button = bible['view1']['btn_share']
share_button.action=share


# Preloading text into a textview called 'thoughts'
with open('instructions.txt','r') as infile:
	thoughts.text = infile.read()

# This lambda function is what allows me to pass arguments to a view's action function. This function is what makes it all work.
f = lambda sender: updates(sender,chapters.data_source,testaments2)

# Quick and dirty query to preload a tableview with an sqlite record.
books.data_source.items = [x[0] for x in sqlite3.connect('bible-sqlite.db').execute('select n from key_english')]
books.data_source.action = f

# Display the bible and restrict its orientation to landscape.
bible.present(orientations=['landscape'],hide_title_bar=True)
intro()
