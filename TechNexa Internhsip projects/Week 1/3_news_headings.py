import requests
from bs4 import BeautifulSoup
from tkinter import *
from tkinter.filedialog import asksaveasfilename
import datetime
import time
import os

def inspect_website_structure(text_widget):
    try:
        urls = ["https://indianexpress.com/" ,"https://www.indiatoday.in/" , "https://news.google.com/"]

        for url in urls:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=10)
            print(response)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all heading tags
                headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                # print("Found Headings:")
                # print("-" * 50)
                
                for heading in headings:  # Show first 10 headings
                    # print(f"Tag: {heading.name}")
                    # print(f"Class: {heading.get('class', 'No class')}")
                    # print(f"ID: {heading.get('id', 'No ID')}")
                    # print(f"Text: {heading.text.strip()[:100]}...")
                    # print("-" * 30)
                    with open("news.txt" , "a" ) as f:
                         f.write(f"{heading.text.strip()}\n\n\n")
                    text_widget.insert("end", f"{heading.text.strip()}\n\n\n") 
                    text_widget.see("end")  
                    time.sleep(1)

    except Exception as e:
             print("error occured as " , e)

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

root = Tk()
root.title("News Headlines")
root.geometry("500x500")
scroll = Scrollbar(root)
scroll.pack(side=RIGHT , fill="y")

str = ''' News Article Page'''
date = datetime.datetime.now()
testvar = None
text_widget = Text(root, wrap=WORD, yscrollcommand=scroll.set, padx=10, pady=10 ,font="Roman 20 bold"  , background="silver", fg="Black") 
text_widget.insert("1.0", f"\t{str}\n\n{date}\n\n\n")
text_widget.pack(fill=BOTH, expand=True)
scroll.config(command=text_widget.yview)

menubar = Menu(root)
m1 = Menu(menubar, tearoff=False)

m1.add_command(label="Save as" , command=save)
menubar.add_cascade(label="File", menu=m1)
root.config(menu=menubar) 

inspect_website_structure(text_widget)
root.mainloop()
    
    


