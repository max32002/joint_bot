#!/usr/bin/env python
#encoding=utf-8

try:
    # for Python2
    from Tkinter import *
    import ttk
    import tkMessageBox as messagebox
except ImportError:
    # for Python3
    from tkinter import *
    from tkinter import ttk
    from tkinter import messagebox

import os
import sys
import json

app_version = "MaxRegBot (2022.02.17)"

homepage_default = u"慈濟首頁 http://www.tzuchi.com.tw/zh/"
homepage_list = (homepage_default
    , u'花蓮慈濟 https://app.tzuchi.com.tw/tchw/opdreg/SecList_HL.aspx'
    , u'玉里慈濟 https://app.tzuchi.com.tw/tchw/OpdReg/SecList_UL.aspx'
    , u'關山慈濟 https://app.tzuchi.com.tw/tchw/OpdReg/SecList_GS.aspx'
    , u'台北慈濟 https://app.tzuchi.com.tw/tchw/OpdReg/SecList_XD.aspx'
    , u'台中慈濟 https://app.tzuchi.com.tw/tchw/OpdReg/SecList_TC.aspx'
    , u'大林慈濟 https://app.tzuchi.com.tw/tchw/OpdReg/SecList_DL.aspx'
    , u'斗六慈濟 https://app.tzuchi.com.tw/tchw/OpdReg/SecList_TL.aspx'
    )

config_filepath = None
config_dict = None

window = None

btn_save = None
btn_exit = None

def load_json():
    # 讀取檔案裡的參數值
    basis = ""
    if hasattr(sys, 'frozen'):
        basis = sys.executable
    else:
        basis = sys.argv[0]
    app_root = os.path.dirname(basis)

    global config_filepath
    config_filepath = os.path.join(app_root, 'settings.json')

    global config_dict
    config_dict = None
    if os.path.isfile(config_filepath):
        with open(config_filepath) as json_data:
            config_dict = json.load(json_data)

def btn_save_clicked():
    btn_save_act()

def btn_save_act(slience_mode=False):

    is_all_data_correct = True

    global config_filepath

    global config_dict
    if not config_dict is None:
        # read user input

        global combo_homepage

        global txt_user_id
        global txt_user_tel
        global txt_dr_name

        if is_all_data_correct:
            if combo_homepage.get().strip()=="":
                is_all_data_correct = False
                messagebox.showerror("Error", "Please enter homepage")
            else:
                config_dict["homepage"] = combo_homepage.get().strip()
    
        if is_all_data_correct:
            if txt_user_id.get().strip()=="":
                is_all_data_correct = False
                messagebox.showerror("Error", "Please enter user id")
            else:
                config_dict["user_id"] = txt_user_id.get().strip()

        if is_all_data_correct:
            if txt_user_tel.get().strip()=="":
                is_all_data_correct = False
                messagebox.showerror("Error", "Please enter user tel")
            else:
                config_dict["user_tel"] = txt_user_tel.get().strip()

        if is_all_data_correct:
            config_dict["dr_name"] = txt_dr_name.get().strip()
            pass

        # save config.
        if is_all_data_correct:
            import json
            with open(config_filepath, 'w') as outfile:
                json.dump(config_dict, outfile)

            if slience_mode==False:
                messagebox.showinfo("File Save", "Done ^_^")

    return is_all_data_correct

def btn_run_clicked():
    if btn_save_act(slience_mode=True):
        import subprocess
        if hasattr(sys, 'frozen'):
            print("execute in frozen mode")
            import platform

            # check platform here.
            # for windows.
            if platform.system() == 'Darwin':
                 subprocess.Popen("./joint.py", shell=True)
            if platform.system() == 'Windows':
                subprocess.Popen("joint.exe", shell=True)
        else:
            #print("execute in shell mode")
            working_dir = os.path.dirname(os.path.realpath(__file__))
            #print("script path:", working_dir)
            #messagebox.showinfo(title="Debug0", message=working_dir)
            try:
                s=subprocess.Popen(['python3', 'joint.py'], cwd=working_dir)
                #s=subprocess.Popen(['./chrome_tixcraft'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=working_dir)
                #s=subprocess.run(['python3', 'chrome_tixcraft.py'], cwd=working_dir)
                #messagebox.showinfo(title="Debug1", message=str(s))
            except Exception as exc:
                try:
                    s=subprocess.Popen(['python', 'joint.py'], cwd=working_dir)
                except Exception as exc:
                    msg=str(exc)
                    messagebox.showinfo(title="Debug2", message=msg)
                    pass


def btn_exit_clicked():
    root.destroy()

def callbackHomepageOnChange(event):
    showHideBlocks()

def showHideBlocks(all_layout_visible=False):
    global UI_PADDING_X

    new_homepage = combo_homepage.get().strip()
    #print("new homepage value:", new_homepage)


def MainMenu(root):
    global UI_PADDING_X
    UI_PADDING_X = 15
    global UI_PADDING_Y
    UI_PADDING_Y = 10

    lbl_homepage = None
    lbl_user_id = None
    lbl_user_tel = None
    lbl_dr_name = None

    homepage = None
    user_id = ""
    user_tel = ""
    dr_name = ""

    global config_dict
    if not config_dict is None:
        # read config.
        if u'homepage' in config_dict:
            homepage = config_dict["homepage"]

        if u'user_id' in config_dict:
            user_id = config_dict[u"user_id"]

        if u'user_tel' in config_dict:
            user_tel = config_dict[u"user_tel"]

        if u'dr_name' in config_dict:
            dr_name = config_dict[u"dr_name"]

        # output config:
        print("homepage", homepage)
        print("user_id", user_id)
        print("user_tel", user_tel)
        print("dr_name", dr_name)

    else:
        print('config is none')

    if homepage is None:
        homepage = homepage_default

    row_count = 0

    frame_group_header = Frame(root)
    group_row_count = 0

    # first row need padding Y
    lbl_homepage = Label(frame_group_header, text="Homepage", pady = UI_PADDING_Y)
    lbl_homepage.grid(column=0, row=group_row_count, sticky = E)

    global combo_homepage
    combo_homepage = ttk.Combobox(frame_group_header, state="readonly")
    combo_homepage['values']= homepage_list
    combo_homepage.set(homepage)
    combo_homepage.bind("<<ComboboxSelected>>", callbackHomepageOnChange)
    combo_homepage.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # Dr Name
    lbl_dr_name = Label(frame_group_header, text="Doctor Name")
    lbl_dr_name.grid(column=0, row=group_row_count, sticky = E)

    global txt_dr_name
    global txt_dr_name_value
    txt_dr_name_value = StringVar(frame_group_header, value=dr_name)
    txt_dr_name = Entry(frame_group_header, width=20, textvariable = txt_dr_name_value)
    txt_dr_name.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # User ID
    lbl_user_id = Label(frame_group_header, text="User ID")
    lbl_user_id.grid(column=0, row=group_row_count, sticky = E)

    global txt_user_id
    global txt_user_id_value
    txt_user_id_value = StringVar(frame_group_header, value=user_id)
    txt_user_id = Entry(frame_group_header, width=20, textvariable = txt_user_id_value)
    txt_user_id.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # User Tel
    lbl_user_tel = Label(frame_group_header, text="User Tel")
    lbl_user_tel.grid(column=0, row=group_row_count, sticky = E)

    global txt_user_tel
    global txt_user_tel_value
    txt_user_tel_value = StringVar(frame_group_header, value=user_tel)
    txt_user_tel = Entry(frame_group_header, width=20, textvariable = txt_user_tel_value)
    txt_user_tel.grid(column=1, row=group_row_count, sticky = W)

    group_row_count+=1

    # add first block to UI.
    frame_group_header.grid(column=0, row=row_count, sticky = W, padx=UI_PADDING_X)
    row_count+=1

    lbl_hr = Label(root, text="")
    lbl_hr.grid(column=0, row=row_count)

    row_count+=1

    frame_action = Frame(root)

    btn_run = ttk.Button(frame_action, text="Run", command=btn_run_clicked)
    btn_run.grid(column=0, row=0)

    btn_save = ttk.Button(frame_action, text="Save", command=btn_save_clicked)
    btn_save.grid(column=1, row=0)

    btn_exit = ttk.Button(frame_action, text="Exit", command=btn_exit_clicked)
    btn_exit.grid(column=2, row=0)

    frame_action.grid(column=0, row=row_count)

def main():
    load_json()

    global root
    root = Tk()
    root.title(app_version)

    #style = ttk.Style(root)
    #style.theme_use('aqua')

    #root.configure(background='lightgray')
    # style configuration
    #style = Style(root)
    #style.configure('TLabel', background='lightgray', foreground='black')
    #style.configure('TFrame', background='lightgray')

    GUI = MainMenu(root)
    GUI_SIZE_WIDTH = 420
    GUI_SIZE_HEIGHT = 200
    GUI_SIZE_MACOS = str(GUI_SIZE_WIDTH) + 'x' + str(GUI_SIZE_HEIGHT)
    GUI_SIZE_WINDOWS=str(GUI_SIZE_WIDTH-60) + 'x' + str(GUI_SIZE_HEIGHT-20)

    GUI_SIZE =GUI_SIZE_MACOS
    import platform
    if platform.system() == 'Windows':
        GUI_SIZE =GUI_SIZE_WINDOWS
    root.geometry(GUI_SIZE)
    root.mainloop()

if __name__ == "__main__":
    main()