import kivy
import csv
import datetime
import sqlite3

from kivy.app import App
from kivy.uix.textinput import TextInput
from functools import partial
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import NumericProperty, ObjectProperty, StringProperty, ReferenceListProperty
from kivy.event import EventDispatcher
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.popup import Popup

server_database_path = "/Users/stefan/CurseCocktailBar/WebsiteFiles/CursedCocktails/db.sqlite3"

token_default = {
        "customer_id":"XXXX",
        "token_id":"XXXXXXXXXX",
        "solved":"XXX",
        "threewords":"WordWordWord",
        "name_id":"namelastnameDD/MM/YY"
        }
drink_default = {
        "drink_id":"XXXX",
        "price":"XXX",
        "discount":"XXX",
        "token_id":"XXXXXXXXXX",
        "solve":"XXX",
        "name":"Drinkname"
        }
admin_default = {
        "token_id":"XXXXXXXXXX",
        "desc":"DRINK_DESC"
        }



tax_rate = 7.25 #IN PERCENTAGE
def setupTables(file_name):

    #Should be CSV
    with open(file_name)  as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            num = row['Table Number']
            seats = row['Seats']
            loc = row['Location (x,y)']
            seat_list = []
            for i in range(int(seats)):
                s = Seat(user_id="",check=[],number=str(i))
                seat_list.append(s)
            table = Table(number=num,seat_list=seat_list,grid=loc)
            tables.append(table)

def readMenu(file_name):

    #Should be CSV
    with open(file_name)  as csv_file:
        csv_reader = csv.DictReader(csv_file)
        cnt = 0
        for row in csv_reader:
            drink = {
                    "Name": row['Name'],
                    "Abbreviation":row["Abbreviation"],
                    "Price":row["Price"],
                    "Category":row["Category"]
                    }
            menu_drinks.append(drink)
            

def initializeRegisterScreen(table_number):
    
    app = App.get_running_app()
    
    table_area = app.root.reg_screen.ids.table_area
    curr_table = tables[table_number]
    table_button = TableButton(table=curr_table)

    seat_len = len(curr_table.seat_list)//2
    if (len(curr_table.seat_list) != 1):
        for seat in curr_table.seat_list[:seat_len]:
            seat_button = SeatButton(seat=seat)
            seat_button.group = "table_area"
            seat_button.text = str(seat.number)
            table_area.add_widget(seat_button) 

    table_button.group = "table_area"
    table_button.text = str(table_number)
    table_button.state = "down"
    table_button.background_color = [0,1,0,1]
    table_area.add_widget(table_button)

    if (len(curr_table.seat_list) != 1):
        for seat in curr_table.seat_list[seat_len:]:
            seat_button = SeatButton(seat=seat)
            seat_button.group = "table_area"
            seat_button.text = str(seat.number)
            table_area.add_widget(seat_button) 

        


class CheckItemPopupLayout(BoxLayout):
    pass

class CheckItemPopup(Popup):
    pass

class CheckItemLayout(BoxLayout):
    pass

def constructInsert(table,default_dict):

    base = "INSERT INTO "
    base += table
    base += "("
    for key in list(default_dict.keys()):
        print(key)
        base += "%s,"%str(key)
    base = base[:-1]
    base += ") VALUES ("
    for value in list(default_dict.values()):
        base += "'%s',"%str(value)
    
    base = base[:-1]
    base += ");"
    print(base)
    return base
class AddTokenItemButton(Button):

    def on_release(self):
        
        new_data = []
        app = App.get_running_app()
        token_view = app.root.token_screen.ids.token_view
        token_toggle_buttons = app.root.token_screen.ids.token_toggle_buttons
        selected = None
        for button in token_toggle_buttons.children:
            if (button.state == "down"):
                selected = button

                
                #Add new item to database
                 
                category = selected.text
                default = ""
                if (category == "Admin"):
                    db_table = "cursedwebsite_admin"
                    default = admin_default
                elif (category == "Drinks"):
                    db_table = "cursedwebsite_drink"
                    default = drink_default
                elif (category == "Tokens"):
                    db_table = "cursedwebsite_customer"
                    default = token_default

                #Update database and reload list
                con = sqlite3.connect(server_database_path)
                cur = con.cursor()

                cmd = constructInsert(db_table,default) 
                print(cmd)
                cur.execute(cmd)
                con.commit()
                con.close()
                #reload recycleview
                button.on_state(button,"down")
        pass 

        pass

class HexTextInput(TextInput):

    def __init__(self, **kwargs):
        super(HexTextInput, self).__init__(**kwargs)
        self.bind(text=self.hexCalc)

    def hexCalc(self,*args):
        num_area = self.parent.children[1] #Might change if layout changes,
        text = args[1]
        #CAREFUL
    
        try:    
            ascii_text = hex(int(text))
            new_text  = str(ascii_text)[2:]
            length = len(new_text)
            for i in range(8-length):
                new_text = "0" + new_text
            new_text = new_text.upper()
            num_area.text = new_text
        except:
           pass
    pass
class SaveButton(Button):

    value = StringProperty()
class EditTextInput(TextInput):

    def update(self,*args):
        save_button = self.parent.parent.ids.save
        save_button.value = self.text


class EditButtonPopupLayout(BoxLayout):
    pass
class EditButtonPopup(Popup):
    db_id = StringProperty()
    def __init__(self,db_id, **kwargs):
        super(EditButtonPopup, self).__init__(**kwargs)
        self.db_id = db_id

class EditButton(Button):
    
    key = StringProperty()
    db_id = StringProperty()

    def __init__(self,key,db_id, **kwargs):
        super(EditButton, self).__init__(**kwargs)
        self.key = key
        self.db_id = db_id

    def on_release(self):
        
        layout = EditButtonPopupLayout()
        popup = EditButtonPopup(title="Change", content=layout,db_id=self.db_id) 
        layout.ids.cb.bind(on_release=popup.dismiss)
        layout.ids.save.bind(on_press=self.save)
        layout.ids.save.bind(on_release=popup.dismiss)
        button_area = layout.ids.edit_popout

        if (self.key == "name"):
            #This is the drink name where we select
            toggle_layout = BoxLayout()
            menu_button = MenuCategoryDatabase(text="B",group="menu")
            menu_button.size_hint = (0.25,1)
            toggle_layout.add_widget(menu_button)
            menu_button = MenuCategoryDatabase(text="R",group="menu")
            menu_button.size_hint = (0.25,1)
            toggle_layout.add_widget(menu_button)
            menu_button = MenuCategoryDatabase(text="G",group="menu")
            menu_button.size_hint = (0.25,1)
            toggle_layout.add_widget(menu_button)
            menu_button = MenuCategoryDatabase(text="Y",group="menu")
            menu_button.size_hint = (0.25,1)
            toggle_layout.add_widget(menu_button)

            button_area.add_widget(toggle_layout)
            box_layout = BoxLayout()
            box_layout.text = "menu_grid"
            button_area.add_widget(box_layout)

        else:
            text_input = EditTextInput(text=self.text) 
            text_input.bind(text=text_input.update)
            button_area.add_widget(text_input)
            if (self.key =="token_id"):
                #add in option to convert to hex
                hex_area = HexTextInput()
                button_area.add_widget(hex_area)
        
        popup.open()

    def save(self,*args):

        button = args[0]
        self.text = button.parent.parent.ids.save.value

        #Find Already selected toggle button 
        app = App.get_running_app()
        token_view = app.root.token_screen.ids.token_view
        token_toggle_buttons = app.root.token_screen.ids.token_toggle_buttons
        selected = None
        category = None
        for button in token_toggle_buttons.children:
            if (button.state == "down"):
                category = button.text
                if (category == "Admin"):
                    db_table = "cursedwebsite_admin"
                elif (category == "Drinks"):
                    db_table = "cursedwebsite_drink"
                elif (category == "Tokens"):
                    db_table = "cursedwebsite_customer"

                #Update database and reload list
                con = sqlite3.connect(server_database_path)
                cur = con.cursor()
                cmd = 'UPDATE %s SET %s = "%s" WHERE id="%d"'%(db_table,self.key,self.text,int(self.db_id))
                print(cmd)
                cur.execute(cmd)
                con.commit()
                cmd = 'SELECT * FROM %s WHERE id= "%d"'%(db_table,int(self.db_id))
                for row in cur.execute(cmd):
                    print(row)
                con.close()
                button.on_state(button,"down") 
                break




class SearchArea(TextInput):
    def __init__(self, **kwargs):
        super(SearchArea, self).__init__(**kwargs)
        self.multiline = False
        self.font_size = self.height - 10
        self.bind(text=self.updateResults)

    def updateResults(self,*args):
        text = args[1]
        new_data = []
        app = App.get_running_app()
        token_view = app.root.token_screen.ids.token_view
        token_toggle_buttons = app.root.token_screen.ids.token_toggle_buttons
        selected = None
        for button in token_toggle_buttons.children:
            if (button.state == "down"):
                selected = button

        for data in selected.data:
            for item in list(data.values()):
                if (text in str(item)):
                    new_data.append(data)
                    break
        token_view.data = new_data
        pass 


class TokenLayoutView(RecycleView):
    def __init__(self, **kwargs):
        super(TokenLayoutView, self).__init__(**kwargs)
        self.data = [
            ]

    def refresh_from_data(self, *largs, **kwargs):
        super(TokenLayoutView,self).refresh_from_data(*largs, **kwargs)


class TokenLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class AdminItemLayout(BoxLayout):
    pass

class AdminItem(RecycleDataViewBehavior, AdminItemLayout):
    ''' Add selection support to the Label '''
    
    index = None
    db_id = ""
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.db_id = str(data['db_id'])
        self.ids.token_id.text = data['token_id'] 
        self.ids.desc.text = data['desc'] 
        return super(AdminItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(AdminItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:

            layout = TokenItemPopupLayout()
            popup = TokenItemPopup(title="Change Data", content=layout) 
            layout.ids.cb.bind(on_release=popup.dismiss)
            layout.ids.delete.bind(on_press=self.delete)
            layout.ids.delete.bind(on_release=popup.dismiss)
            button_area = layout.ids.token_popout
            button\
            = EditButton(text=self.ids.token_id.text,key="token_id",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.desc.text,key="desc",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            
            popup.open()
            return self.parent.select_with_touch(self.index, touch)

    def delete(self,*args):
        
        #Find Already selected toggle button 
        app = App.get_running_app()
        token_view = app.root.token_screen.ids.token_view
        token_toggle_buttons = app.root.token_screen.ids.token_toggle_buttons
        selected = None
        category = None
        for button in token_toggle_buttons.children:
            if (button.state == "down"):
                category = button.text
                if (category == "Admin"):
                    db_table = "cursedwebsite_admin"
                elif (category == "Drinks"):
                    db_table = "cursedwebsite_drink"
                elif (category == "Tokens"):
                    db_table = "cursedwebsite_customer"

                #Update database and reload list
                con = sqlite3.connect(server_database_path)
                cur = con.cursor()
                cmd = 'DELETE FROM %s WHERE id="%d"'%(db_table,int(self.db_id))
                cur.execute(cmd)
                con.commit()
                con.close()
                button.on_state(button,"down") 
                break


        
        pass

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.layout_manager.clear_selection()
        else:
            pass

class DrinkItemLayout(BoxLayout):
    pass

class DrinkItem(RecycleDataViewBehavior, DrinkItemLayout):
    ''' Add selection support to the Label '''
    
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids.drink_id.text = data['drink_id'] 
        self.ids.price.text = data['price'] 
        self.ids.discount.text = data['discount'] 
        self.ids.token_id.text = data['token_id'] 
        self.ids.solve.text = data['solve'] 
        self.ids.name.text = data['name'] 
        return super(DrinkItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(DrinkItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:

            layout = TokenItemPopupLayout()
            popup = TokenItemPopup(title="Change Data", content=layout) 
            layout.ids.cb.bind(on_release=popup.dismiss)
            layout.ids.delete.bind(on_press=self.delete)
            layout.ids.delete.bind(on_release=popup.dismiss)
            button_area = layout.ids.token_popout
            button\
            = EditButton(text=self.ids.drink_id.text,key="drink_id",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.price.text,key="price",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.discount.text,key="discount",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.token_id.text,key="token_id",db_id=str(self.db_id)) 
            button.size_hint = (3,1)
            button_area.add_widget(button)

            button\
            = EditButton(text=self.ids.solve.text,key="solve",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.name.text,key="name",db_id=str(self.db_id)) 
            button.size_hint = (2,1)
            button_area.add_widget(button)
            
            popup.open()
            return self.parent.select_with_touch(self.index, touch)

    def delete(self,*args):
        
        #Find Already selected toggle button 
        app = App.get_running_app()
        token_view = app.root.token_screen.ids.token_view
        token_toggle_buttons = app.root.token_screen.ids.token_toggle_buttons
        selected = None
        category = None
        for button in token_toggle_buttons.children:
            if (button.state == "down"):
                category = button.text
                if (category == "Admin"):
                    db_table = "cursedwebsite_admin"
                elif (category == "Drinks"):
                    db_table = "cursedwebsite_drink"
                elif (category == "Tokens"):
                    db_table = "cursedwebsite_customer"

                #Update database and reload list
                con = sqlite3.connect(server_database_path)
                cur = con.cursor()
                cmd = 'DELETE FROM %s WHERE id="%d"'%(db_table,int(self.db_id))
                cur.execute(cmd)
                con.commit()
                con.close()
                button.on_state(button,"down") 
                break
    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.layout_manager.clear_selection()
        else:
            pass

class TokenItemPopupLayout(BoxLayout):
    pass

class TokenItemPopup(Popup):
    pass

class TokenItemLayout(BoxLayout):
    pass

class TokenItem(RecycleDataViewBehavior, TokenItemLayout):
    ''' Add selection support to the Label '''
    
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.ids.customer_id.text = data['customer_id'] 
        self.ids.token_id.text = data['token_id'] 
        self.ids.solved.text = data['solved'] 
        self.ids.threewords.text = data['threewords'] 
        self.ids.name_id.text = data['name_id'] 
        self.ids.half_solved.text = data['half_solved'] 
        return super(TokenItem, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(TokenItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:

            layout = TokenItemPopupLayout()
            popup = TokenItemPopup(title="Change Data", content=layout) 
            layout.ids.cb.bind(on_release=popup.dismiss)
            layout.ids.delete.bind(on_press=self.delete)
            layout.ids.delete.bind(on_release=popup.dismiss)
            button_area = layout.ids.token_popout
            button\
            = EditButton(text=self.ids.customer_id.text,key="customer_id",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.token_id.text,key="token_id",db_id=str(self.db_id)) 
            button.size_hint = (3,1)
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.half_solved.text,key="half_solved",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.solved.text,key="solved",db_id=str(self.db_id)) 
            button_area.add_widget(button)
            button\
            = EditButton(text=self.ids.threewords.text,key="threewords",db_id=str(self.db_id)) 
            button.size_hint = (3,1)
            button_area.add_widget(button)

            button\
            = EditButton(text=self.ids.name_id.text,key="name_id",db_id=str(self.db_id)) 
            button.size_hint = (3,1)
            button_area.add_widget(button)
            
            popup.open()
            return self.parent.select_with_touch(self.index, touch)

    def delete(self,*args):
        
        #Find Already selected toggle button 
        app = App.get_running_app()
        token_view = app.root.token_screen.ids.token_view
        token_toggle_buttons = app.root.token_screen.ids.token_toggle_buttons
        selected = None
        category = None
        for button in token_toggle_buttons.children:
            if (button.state == "down"):
                category = button.text
                if (category == "Admin"):
                    db_table = "cursedwebsite_admin"
                elif (category == "Drinks"):
                    db_table = "cursedwebsite_drink"
                elif (category == "Tokens"):
                    db_table = "cursedwebsite_customer"

                #Update database and reload list
                con = sqlite3.connect(server_database_path)
                cur = con.cursor()
                cmd = 'DELETE FROM %s WHERE id="%d"'%(db_table,int(self.db_id))
                cur.execute(cmd)
                con.commit()
                con.close()
                button.on_state(button,"down") 
                break
    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.layout_manager.clear_selection()
        else:
            pass

class TokenToggleButton(ToggleButton):
    #We store the database values inside this object

    data = []
    def __init__(self, **kwargs):
        super(TokenToggleButton, self).__init__(**kwargs)
        self.allow_no_selection = False
        Clock.schedule_once(self._finish_init)

    def _finish_init(self,dt):
        if (self.text == "Tokens"):
            self.state = "down"

    def on_state(self, widget, value):
        if value == "down":
            self.data = []
            self.fillData(widget)
            pass
        else:
            pass

    def fillData(self,widget):
        #Go to database and query for all values needed

        #depending on our Text field we query what we need

        text = self.text
        if (text == "Tokens"):

            #This is the data we get
            con = sqlite3.connect(server_database_path)
            cur = con.cursor()
            cmd = "SELECT * FROM cursedwebsite_customer;"

            for row in cur.execute(cmd):
                token = {}
                token["type"] = "token"
                token["db_id"] = row[0] 
                token["customer_id"] = row[1] 
                token["token_id"] = row[2] 
                token["solved"] = row[3] 
                token["threewords"] = row[4] 
                token["name_id"] = row[5] 
                token["half_solved"] = row[6] 
                
                self.data.append(token)

            con.close()
            
            app = App.get_running_app()
            token_view = app.root.token_screen.ids.token_view
            token_view.viewclass = "TokenItem" 
            token_view.data = self.data
        elif (text == "Drinks"):

            #This is the data we get
            con = sqlite3.connect(server_database_path)
            cur = con.cursor()
            cmd = "SELECT * FROM cursedwebsite_drink;"

            for row in cur.execute(cmd):
                token = {}
                token["type"] = "drink"
                token["db_id"] = row[0] 
                token["drink_id"] = row[1] 
                token["price"] = row[2] 
                token["discount"] = row[3] 
                token["token_id"] = row[4] 
                token["solve"] = row[5] 
                token["name"] = row[6] 
                
                self.data.append(token)

            con.close()
            app = App.get_running_app()
            token_view = app.root.token_screen.ids.token_view
            token_view.viewclass = "DrinkItem" 
            token_view.data = self.data

        elif (text == "Admin"):

            #This is the data we get
            con = sqlite3.connect(server_database_path)
            cur = con.cursor()
            cmd = "SELECT * FROM cursedwebsite_admin;"

            for row in cur.execute(cmd):
                token = {}
                token["type"] = "admin"
                token["db_id"] = row[0] 
                token["token_id"] = row[1] 
                token["desc"] = row[2] 
                
                self.data.append(token)

            con.close()
            app = App.get_running_app()
            token_view = app.root.token_screen.ids.token_view
            token_view.viewclass = "AdminItem" 
            token_view.data = self.data

class MenuCategoryToggleButton(ToggleButton):
    
    def __init__(self, **kwargs):
        super(MenuCategoryToggleButton, self).__init__(**kwargs)
        self.menu_buttons = []
    

    def addItem(self,button):
        app = App.get_running_app()
        number = "X"
        for widget in app.root.reg_screen.ids.table_area.children:
            if type(widget) == SeatButton:
                if (widget.state == "down"):
                    number = str(widget.seat.number)
                    break
        time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S,%f") 
        check = {"drink_name":button.drink.name,
                "drink_price":button.drink.price,
                "drink_quantity":"1",
                "assigned_seat":number,
                "time": time
                }
        app.root.reg_screen.ids.check_view.data.append(check)
        for widget in app.root.reg_screen.ids.table_area.children:
            if type(widget) == SeatButton:
                if (widget.state == "down"):
                    widget.seat.check.append(check)
                    break
            elif type(widget) == TableButton:
                if (widget.state == "down"):
                    widget.table.check.append(check)
                    break
        pass
    def on_state(self, widget, value):
        if value == "down":
            val = self.text
            app = App.get_running_app()
            menu_grid = app.root.reg_screen.ids.menu_grid

            self.menu_buttons = []
            for drink in menu_drinks:
                if drink["Category"] == val:
                    
                    d = Drink(
                        name = drink["Name"],
                        abbreviation= drink["Abbreviation"],
                        price = drink["Price"],
                        category = drink["Category"])
                    button = MenuButton(drink=d)
                    button.bind(on_press=self.addItem)
                    self.menu_buttons.append(button)
                    menu_grid.add_widget(button)

        else:
            app = App.get_running_app()
            menu_grid = app.root.reg_screen.ids.menu_grid
            for button in self.menu_buttons:
                menu_grid.remove_widget(button)

class MenuCategoryDatabase(MenuCategoryToggleButton):

    def changeItem(self, menu_button):

        #Find Already selected toggle button 
        app = App.get_running_app()
        token_view = app.root.token_screen.ids.token_view
        token_toggle_buttons = app.root.token_screen.ids.token_toggle_buttons
        selected = None
        category = None
        for button in token_toggle_buttons.children:
            if (button.state == "down"):
                category = button.text
                if (category == "Admin"):
                    db_table = "cursedwebsite_admin"
                elif (category == "Drinks"):
                    db_table = "cursedwebsite_drink"
                elif (category == "Tokens"):
                    db_table = "cursedwebsite_customer"

                #Update database and reload list
                name = menu_button.drink.name
                price = menu_button.drink.price
                popup = self.parent.parent.parent.parent.parent.parent
                db_id = popup.db_id  
                con = sqlite3.connect(server_database_path)
                cur = con.cursor()
                cmd = 'UPDATE %s SET name = "%s" WHERE id="%d"'%(db_table,name,int(db_id))
                print(cmd)
                cur.execute(cmd)
                cmd = 'UPDATE %s SET price = "%s" WHERE id="%d"'%(db_table,price,int(db_id))
                print(cmd)
                cur.execute(cmd)
                con.commit()
                cmd = 'SELECT * FROM %s WHERE id= "%d"'%(db_table,int(db_id))
                for row in cur.execute(cmd):
                    print(row)
                con.close()
                button.on_state(button,"down") 
                self.parent.parent.parent.ids.save.value = name
                
                break



        pass

    def on_state(self, widget, value):
        if value == "down":
            val = self.text
            menu_grid = None
            for widget in self.parent.parent.children:
                if (widget.text== "menu_grid"):
                    menu_grid = widget
                    break
            if (menu_grid == None): return

            self.menu_buttons = []
            for drink in menu_drinks:
                if drink["Category"] == val:
                    
                    d = Drink(
                        name = drink["Name"],
                        abbreviation= drink["Abbreviation"],
                        price = drink["Price"],
                        category = drink["Category"])
                    button = MenuButton(drink=d)
                    button.bind(on_press=self.changeItem)
                    self.menu_buttons.append(button)
                    menu_grid.add_widget(button)

        else:
            menu_grid = None
            for widget in self.parent.parent.children:
                if (widget.text == "menu_grid"):
                    menu_grid = widget
                    break
            if (menu_grid == None): return
            for button in self.menu_buttons:
                menu_grid.remove_widget(button)
    pass

class MenuButton(Button):
    def __init__(self, drink, **kwargs):
        super(MenuButton, self).__init__(**kwargs)
        self.drink = drink 
        self.text = drink.abbreviation
    
class Drink(object):
    def __init__(self, name, abbreviation,price,category, **kwargs):
        super(Drink, self).__init__(**kwargs)
        self.name = name 
        self.abbreviation = abbreviation 
        self.price = price 
        self.category = category 

class SeatButton(ToggleButton):
    
    def __init__(self, seat, **kwargs):
        super(SeatButton, self).__init__(**kwargs)
        self.seat = seat
        self.allow_no_selection = False
    def on_state(self, widget, value):

        if value == "down":
            #populate check_view with current check
            app = App.get_running_app()
            check_view = app.root.reg_screen.ids.check_view
            check_view.data = self.seat.check
            #Change Symbolarea + customer_id to match seated person from DB
            
            table_num = app.root.table_screen.selected_table
            
            con = sqlite3.connect(server_database_path)
            cur = con.cursor()
            cmd = 'SELECT * FROM cursedwebsite_table WHERE number= %d'%table_num 
            board_id = 0
            seat_num = int(self.text) + 1 #Seat numbers start 0, table boards start 1
            for row in cur.execute(cmd):
                board_id = row[seat_num+1]
            cmd = 'SELECT * FROM cursedwebsite_board WHERE id = %d'%board_id
            token = ""
            half_solved = 0
            solved = 0
            for row in cur.execute(cmd):
                token = row[2]
                half_solved = int(row[4])
                solved = int(row[6])
            half_solved_set = set()
            solved_set = set()
            for i in range(1,9):
                if (half_solved & 0x1): 
                    half_solved_set.add(i)
                if (solved & 0x1):
                    solved_set.add(i)
                half_solved >>= 1
                solved >>= 1

            for child in app.root.reg_screen.ids.symbols_half_solved.children:
                if (int(child.text) in half_solved_set): child.background_color = [0,0,1,1]
                else: child.background_color = [1,1,1,1]
            for child in app.root.reg_screen.ids.symbols_solved.children:
                if (int(child.text) in solved_set): child.background_color = [1,0,1,1]
                else: child.background_color = [1,1,1,1]

            app.root.reg_screen.ids.seat_customer_id.text = token
            con.commit()
            con.close()

        else:
            pass
class Seat(object):
    def __init__(self, user_id,check,number, **kwargs):
        super(Seat, self).__init__(**kwargs)
        self.user_id = user_id 
        self.number = number
        #check is a list of CheckItems
        self.check = check

class TableAssignButton(Button):
    def __init__(self, table, **kwargs):
        super(TableAssignButton, self).__init__(**kwargs)
        self.table = table
    pass
class SeatAssignButton(Button):
    def __init__(self, seat, **kwargs):
        super(SeatAssignButton, self).__init__(**kwargs)
        self.seat = seat
    pass

class TableButton(ToggleButton): 
    def __init__(self, table, **kwargs):
        super(TableButton, self).__init__(**kwargs)
        self.table = table
        self.allow_no_selection = False

    def on_state(self, widget, value):

        app = App.get_running_app()
        check_view = app.root.reg_screen.ids.check_view
        if value == "down":
            #populate check_view with current check of all seats
            check_view.data = self.table.check
            for seat in self.table.seat_list:
                if (len(seat.check) != 0):
                    for item in seat.check:
                        check_view.data.append(item)
        else:
            #populate seat opject with check
            pass
class Table(object):
    def __init__(self, number,seat_list,grid, **kwargs):
        super(Table, self).__init__(**kwargs)
        self.number = number
        self.check = []
        self.grid = grid

        #list of Seat objects
        self.seat_list = seat_list
        self.seat_amt = len(seat_list)

class SymbolArea(BoxLayout):
    pass
class CheckItem(RecycleDataViewBehavior, CheckItemLayout):
    ''' Add selection support to the Label '''
    
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        if (len(data) != 0):
            self.ids.drink_name.text = data['drink_name'] 
            self.ids.drink_quantity.text = data['drink_quantity'] 
            self.ids.assigned_seat.text = data["assigned_seat"]
            self.ids.drink_price.text = "$%s"%data['drink_price'] 

        return super(CheckItem, self).refresh_view_attrs(
            rv, index, data)


    def deleteData(self,button):
        app = App.get_running_app()
        check_view = app.root.reg_screen.ids.check_view
        item = check_view.data[self.index]
        for widget in app.root.reg_screen.ids.table_area.children:
            if type(widget) == SeatButton:
                for check_item in widget.seat.check:
                    if check_item['time']== item['time']:
                        widget.seat.check.remove(check_item)
            elif type(widget) == TableButton:
                for check_item in widget.table.check:
                    if check_item['time']== item['time']:
                        widget.table.check.remove(check_item)
        del check_view.data[self.index]


    def assignSeat(self,button):

        #When we want to change the assign seat we del the prev data and re add
        # it to the correct check

        #We save the check data so we can re add it later
        app = App.get_running_app()
        check_view = app.root.reg_screen.ids.check_view
        item = check_view.data[self.index]

        #delete old data
        self.deleteData(button)

        #just add to appropriate check and refresh the check view

        number = button.text
        item['assigned_seat'] = number
        for widget in app.root.reg_screen.ids.table_area.children:
            if type(widget) == SeatButton:
                if (number == str(widget.seat.number)):
                    widget.seat.check.append(item)
                    break
            elif type(widget) == TableButton:
                if (number == "X"):
                    widget.table.check.append(item)
                    break

        #reload current selected toggle button
        for widget in app.root.reg_screen.ids.table_area.children:
            if widget.state == "down":
                widget.on_state(widget,"down")
        

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(CheckItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            app = App.get_running_app()
            layout = CheckItemPopupLayout()
            assign_layout = layout.ids.assign_seat
            table_area = app.root.reg_screen.ids.table_area
            popup = CheckItemPopup(title="demo", content=layout) 
             
            for widget in reversed(table_area.children):
                if type(widget) == SeatButton:
                    seat_button = SeatAssignButton(seat=widget.seat)
                    seat_button.text = str(widget.seat.number)
                    seat_button.bind(on_press=self.assignSeat,on_release=popup.dismiss)
                    assign_layout.add_widget(seat_button)

                elif type(widget) == TableButton:
                    table_button = TableAssignButton(table=widget.table)
                    table_button.text = "X"
                    table_button.bind(on_press=self.assignSeat,on_release=popup.dismiss)
                    assign_layout.add_widget(table_button)

            layout.ids.cb.bind(on_release=popup.dismiss)
            layout.ids.delete.bind(on_press=self.deleteData,on_release=popup.dismiss)
            layout.ids.check_item.ids.drink_name.text =  self.ids.drink_name.text
            layout.ids.check_item.ids.drink_price.text =  self.ids.drink_price.text
            layout.ids.check_item.ids.drink_quantity.text =  self.ids.drink_quantity.text
            layout.ids.check_item.ids.assigned_seat.text =  self.ids.assigned_seat.text
            popup.open()
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            rv.layout_manager.clear_selection()
        else:
            pass

class CheckLayoutView(RecycleView):
    def __init__(self, **kwargs):
        super(CheckLayoutView, self).__init__(**kwargs)
        self.data = [
            ]

    def refresh_from_data(self, *largs, **kwargs):
        super(CheckLayoutView,self).refresh_from_data(*largs, **kwargs)

        #Going to update the total 
        app = App.get_running_app()
        try: subtotal_label = app.root.reg_screen.ids.subtotal
        except: return
        subtotal = 0.00
        for check in self.data:
            subtotal += float(check['drink_price'])
        subtotal_label.text = "Subtotal: $%s"%str(subtotal)
        
        #update Tax and Total
        tax = subtotal * (tax_rate/100)        
        tax = round(tax,2)

        total = subtotal + tax
        tax_label = app.root.reg_screen.ids.tax
        tax_label.text = "Tax: $%s"%str(tax)
        total_label = app.root.reg_screen.ids.total
        total_label.text = "Total: $%s"%str(total)

class CheckLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class RegisterScreen(Screen):

    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self,dt):
        self.ids.back_button.bind(on_release=self.changeScreen)
    
    def on_enter(self):
        table_num = self.manager.get_screen("table_screen").selected_table
        initializeRegisterScreen(table_num)
        

    def changeScreen(self, *args):
        #Save current table into global tables[]
        num = self.manager.get_screen("table_screen").selected_table
        table_area = self.ids.table_area
        check_view = self.ids.check_view


        for child in table_area.children:
            if(type(child) == TableButton):
                tables[num] = child.table
                break
        table_area.clear_widgets()
        check_view.data = []
        self.manager.current = "table_screen"

    pass

class TableScreen(Screen):

    selected_table = NumericProperty(1)

    def __init__(self, **kwargs):
        super(TableScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self,dt):
        self.selected_table = 0
        for table in tables:
            row = int(table.grid[0]) #indexing into string "x,y"
            col = int(table.grid[2])
            button = TableGridButton(row=row,column=col,text=table.number)
            button.bind(on_release= partial(self.selectTable,int(table.number)))
            self.ids.table_grid.add_widget(button)
        self.ids.back_button.bind(on_release=self.changeScreen)

    def on_enter(self):
        #Update all tables to correct color
        occupied = []
        for table in tables:
            if (len(table.check) != 0):
                occupied.append(table.number)
                continue
            for seat in table.seat_list:
                if (len(seat.check) != 0):
                    occupied.append(table.number)
                    break
        for table_button in self.ids.table_grid.children:
            if (table_button.text in occupied):
                table_button.background_color = (1,0,0,1)
            else:
                table_button.background_color = (0,1,0,1)


    def changeScreen(self,*args):
        self.manager.current = "menu_screen"

    def selectTable(self,table_number,button):
        self.selected_table = table_number
        self.manager.current = "reg_screen"

class TokenScreen(Screen):

    def __init__(self, **kwargs):
        super(TokenScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self,dt):
        self.ids.back_button.bind(on_release=self.changeScreen)
        
    def changeScreen(self,*args):
        self.manager.current = "menu_screen"


class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        Clock.schedule_once(self._finish_init)

    def _finish_init(self,dt):
        self.ids.table_button.bind(on_release=self.changeScreen)
        self.ids.token_button.bind(on_release=self.changeScreen)

    def changeScreen(self, *args):
        button = args[0]
        if (button.text == "Token Screen"):
            self.manager.current = "token_screen"
        elif (button.text == "Table Screen"):
            self.manager.current = "table_screen"


class POSApp(App):

    def build(self):
        setupTables("CurseTableSetup.csv")
        m = Manager(transition=NoTransition())
        return m

class Manager(ScreenManager):
    menu_screen = ObjectProperty(None)
    reg_screen = ObjectProperty(None)

menu_drinks = []
tables= []
        

#   Credit to Incliment for spareGridLayout code : https://github.com/inclement/sparsegridlayout
#   Check him out
#
########BEGIN#############
class SparseGridLayout(FloatLayout):

    rows = NumericProperty(1)
    columns = NumericProperty(1)
    shape = ReferenceListProperty(rows, columns)

    def do_layout(self, *args):
        shape_hint = (1. / self.rows, 1. / self.columns)
        for child in self.children:
            child.size_hint = shape_hint
            if not hasattr(child, 'row'):
                child.row = 0
            if not hasattr(child, 'column'):
                child.column = 0

            child.pos_hint = {'x': shape_hint[0] * child.column,
                              'y': shape_hint[1] * child.row}
        super(SparseGridLayout, self).do_layout(*args)

class GridEntry(EventDispatcher):
    row = NumericProperty(0)
    column = NumericProperty(0)

class TableGridButton(Button, GridEntry):
    
    pass


##########END###############

if __name__ == "__main__":

    readMenu("CurseMenu.csv")
    POSApp().run()




