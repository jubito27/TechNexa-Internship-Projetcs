from tkinter import messagebox
from tkinter import *
import os
from tkinter.filedialog import askopenfilename , asksaveasfilename
from collections import Counter


def dark():
    root.configure(background="#302f2e")
    text_widget.configure(background="#302f2e" , foreground='white')
    scroll.configure(bg="#302f2e", fg='white') 
    menubar.configure(background="#302f2e" , foreground='white' , bg="#302f2e" , fg='white')

def light():
    root.configure(background="white")
    text_widget.configure(background="white" , foreground='#000000')

def new():
    global testvar
    root.title("Untitled - notepad")
    testvar = None
    text_widget.delete(1.0 , END)

def save():
    global testvar
    if testvar is None:
        testvar = asksaveasfilename(initialfile="Untitled.txt", defaultextension=".txt", filetypes=[(".txt", "*.*"), ("Text Documents", "*.txt")])
        if testvar == "":
            testvar = None
        else:
            with open(testvar, "w") as f:
                f.write(text_widget.get(1.0, END))  # Write content of text_widget to the file
            root.title(os.path.basename(testvar) + " - notepad")
    else:
        with open(testvar, "w") as f:
            f.write(text_widget.get(1.0, END))  # Write content of text_widget to the file

def open_file():
    global testvar
    testvar = askopenfilename(defaultextension=".txt", filetypes=[("All types", "*.*"), ("Text Documents", "*.txt")])

    if testvar == "":
        testvar = None
    else:
        root.title(os.path.basename(testvar) + " .txt")
        text_widget.delete(1.0, END)
        with open(testvar, "r") as f:
            text_widget.insert(1.0, f.read())


def letters_count():
    global text_widget
    words =  text_widget.get("1.0" , "end-1c")
    wordcount = []
    
    for text in words:
        wordcount.append(text)
    
    filtered_list = [item for item in wordcount if item != ' ']
    print(wordcount)
    print(filtered_list)
    totalwords = len(filtered_list)
   
    messagebox.showinfo("Words Count" , f"Total words are {totalwords}")

def duplicate_letters():
    global  text_widget
    words =  text_widget.get("1.0" , "end-1c")

    wordcount = []
    
    for text in words:
        wordcount.append(text)
    
    filtered_list = [item for item in wordcount if item != ' ']
    counter = Counter(filtered_list)
    messagebox.showinfo("Duplicate words" , f"List of words are\n{counter}")

def words_count():
    global text_widget
    words =  text_widget.get("1.0" , "end-1c")
    wordcount = words.split()
    messagebox.showinfo("Words Count" , f"Total words are {len(wordcount)}")

def duplicate_words():
    global text_widget
    words =  text_widget.get("1.0" , "end-1c")
    wordcount= words.split()

    counter = Counter(wordcount)
    messagebox.showinfo("Duplicate words" , f"List of words are\n{counter}")
                
        

root = Tk()
root.geometry("400x400")
root.title('Text Files Reader')

frame =Frame(root , padx=22 , pady=32 ).pack(fill=Y , )
str = ''' Hey there its abhishek sharma'''
scroll =Scrollbar(root)
scroll.pack(side=RIGHT , fill=Y)

testvar = None
text_widget = Text(frame, wrap=WORD, yscrollcommand=scroll.set, padx=10, pady=10 ,font="serif 10 bold")
text_widget.insert(INSERT, str)
text_widget.pack(fill=BOTH, expand=True)
scroll.config(command=text_widget.yview)

menubar = Menu(root)
m1 = Menu(menubar, tearoff=False)
m1.add_command(label="New" , command=new)
m1.add_command(label="Open" , command=open_file)
m1.add_command(label="Save" , command=save)
m1.add_command(label="Save as" , command=save)
menubar.add_cascade(label="File", menu=m1)

m2 = Menu(menubar, tearoff=False)
m2.add_command(label="Dark Theme" , command=dark)
m2.add_command(label="Light Theme", command=light)
menubar.add_cascade(label="View", menu=m2)

m3 = Menu(menubar , tearoff=False)
m3.add_command(label="Letters count" , command=letters_count)
m3.add_command(label="duplicate Letters" , command=duplicate_letters)
m3.add_command(label="duplicate words" , command=duplicate_words)
m3.add_command(label="words count" , command=words_count)
menubar.add_cascade(label="Text Formate" , menu=m3)
root.config(menu=menubar) 




root.mainloop()