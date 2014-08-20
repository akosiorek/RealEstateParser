#!/usr/bin/python

import Tkinter, tkFileDialog

class simpleapp_tk(Tkinter.Tk):
	def __init__(self,parent):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.initialize()
		
	def initialize(self):
		self.grid()
		
		self.text1 = Tkinter.StringVar()
		label1 = Tkinter.Label(self,fg="black",bg="green",textvariable=self.text1)
		label1.grid(column=0,row=0,columnspan=3,sticky='EW')

		button1 = Tkinter.Button(self,text=u"Otworz plik",command=self.OpenFileName)
		button1.grid(column=4,row=0)
		
		self.text2 = Tkinter.StringVar()
		label2 = Tkinter.Label(self,fg="black",bg="green",textvariable=self.text2)
		label2.grid(column=0,row=1,columnspan=3,sticky='EW')

		button2 = Tkinter.Button(self,text=u"Zapisz",command=self.SaveFileName)
		button2.grid(column=4,row=1)	
		
		self.grid_columnconfigure(0,weight=1)
		self.resizable(True,False)

		self.file_opt = options = {}
		options['defaultextension'] = '.txt'
		options['filetypes'] = [('text file', '.txt'), ('output file','.csv'), ('all files','.*')]
		options['initialdir'] = 'C:\\'
		
	def OnButtonClick(self):
		print "Procced entry"

	def OpenFileName(self):
		self.openFile = tkFileDialog.askopenfilenames(**self.file_opt)
		self.text1.set(self.openFile)
		print self.tk.splitlist(self.openFile)

	def SaveFileName(self):
		self.saveFile = tkFileDialog.asksaveasfilename(**self.file_opt)
		self.text2.set(self.saveFile)
		
if __name__=="__main__":
	app = simpleapp_tk(None)
	app.title("program")
	app.mainloop()