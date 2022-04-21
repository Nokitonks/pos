import kivy
import csv
import datetime

from kivy.app import App
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty, StringProperty
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
    for seat in curr_table.seat_list[:seat_len]:
        seat_button = SeatButton(seat=seat)
        seat_button.group = "table_area"
        table_area.add_widget(seat_button) 

    table_button.group = "table_area"
    table_button.text = str(table_number)
    table_button.state = "down"
    table_area.add_widget(table_button)

    for seat in curr_table.seat_list[seat_len:]:
        seat_button = SeatButton(seat=seat)
        seat_button.group = "table_area"
        table_area.add_widget(seat_button) 

        


class CheckItemPopupLayout(BoxLayout):
    pass

class CheckItemPopup(Popup):
    pass

class CheckItemLayout(BoxLayout):
    pass

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
        time = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") 
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

        else:
            pass
class Seat(object):
    def __init__(self, user_id,check,number, **kwargs):
        super(Seat, self).__init__(**kwargs)
        self.user_id = user_id 
        self.number = number
        #check is a list of CheckItems
        self.check = check


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
    def __init__(self, number,seat_list, **kwargs):
        super(Table, self).__init__(**kwargs)
        self.number = number
        self.check = []

        #list of Seat objects
        self.seat_list = seat_list
        self.seat_amt = len(seat_list)




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
            self.ids.drink_price.text = data['drink_price'] 
            self.ids.assigned_seat.text = data["assigned_seat"]
        return super(CheckItem, self).refresh_view_attrs(
            rv, index, data)


    def deleteData(self,button):
        print("Del")
        app = App.get_running_app()
        check_view = app.root.reg_screen.ids.check_view
        item = check_view.data[self.index]
        print(item)
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



    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(CheckItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            layout = CheckItemPopupLayout()
            popup = CheckItemPopup(title="demo", content=layout) 
            layout.ids.cb.bind(on_release=popup.dismiss)
            layout.ids.delete.bind(on_press=self.deleteData,on_release=popup.dismiss)
            layout.ids.check_item.ids.drink_name.text =  self.ids.drink_name.text
            layout.ids.check_item.ids.drink_price.text =  self.ids.drink_price.text
            layout.ids.check_item.ids.drink_quantity.text =  self.ids.drink_quantity.text
            popup.open()
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
            rv.layout_manager.clear_selection()
        else:
            print("selection removed for {0}".format(rv.data[index]))

class CheckLayoutView(RecycleView):
    def __init__(self, **kwargs):
        super(CheckLayoutView, self).__init__(**kwargs)
        self.data = [
            ]

class CheckLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    pass

class RegisterScreen(Screen):

    def __init__(self, **kwargs):
        super(RegisterScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        initializeRegisterScreen(0)


    pass

class MenuScreen(Screen):

    def on_enter(self, *args):
        Clock.schedule_once(self.changeScreen, 0.5)

    def changeScreen(self, *args):
        self.manager.current = "reg_screen"


class POSApp(App):

    def build(self):
        m = Manager(transition=NoTransition())
        return m

class Manager(ScreenManager):
    menu_screen = ObjectProperty(None)
    reg_screen = ObjectProperty(None)

menu_drinks = []
tables= [Table(number=0,seat_list=[Seat("A700",[],0),Seat("A700",[],1),Seat("A700",[],2),Seat("1281000AB",[],3)])]

if __name__ == "__main__":

    readMenu("CurseMenu.csv")
    POSApp().run()




