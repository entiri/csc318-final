import os
import kivy
from kivy.app import App
from kivy.core.image import Image
from kivy.core.window import Window
Window.clearcolor = (0.75, 0.75, 0.75, 1)
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.checkbox import CheckBox
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, StringProperty, \
     NumericProperty, ListProperty
from functools import partial

class AppScreen(FloatLayout):
    app = ObjectProperty(None)

class MainMenu(AppScreen):
    pass

class SettingScreen(TabbedPanel):
    app = ObjectProperty(None)

    def back_to_main(self):
        '''
        Direct the user back to the main page
        '''
        self.app.goto_screen("menu")

class CSCGroupNineApp(App):
    data = StringProperty('')
    searchHistory = StringProperty('')
    
    # (ignore/saved/favorites)List are used to store instances in for saved/ignore tabs.
    ignoreList = ListProperty([])
    historyList = ListProperty([])
    favoritesList = ListProperty([])

    def build(self):
        self.screens = {}
        self.screens["settings"] = SettingScreen(app=self)
        self.screens["menu"] = MainMenu(app=self)
        self.root = FloatLayout()
        self.goto_screen("menu")
        return self.root
 
    def goto_screen(self, screen_name):
        self.root.clear_widgets()
        self.root.add_widget(self.screens[screen_name])
        
    def results(self, query):
        '''
        Return a list of all search results for index in fle
        '''

        if len(query) <= 2:
            query = 'NULL'

        # If the user had previously made a search, delete the result.
        for child in self.screens["menu"].ids.search.children:
            if child.id in ['noResults']:
                self.screens["menu"].ids.search.remove_widget(child)
            elif child.id in ['tooManyResults']:
                self.screens["menu"].ids.search.remove_widget(child)
            elif child.id in ['scroll']:
                self.screens["menu"].ids.search.remove_widget(child)

        #Assume the text may not be all lowercase words, change it so that it can be
        # (change to title case)
        query = query.lower()

        #open file
        fle = open(os.path.dirname(os.path.realpath(__file__)) + '\\idioms.txt',\
                   'r')

        queryRslt = []

        # Use this to determine if a result should be shown or not 
        ignoreLst =[]
        for i in self.ignoreList:
            ignoreLst.append(i[0])

        #The toggle is only flipped when lines are to be added to queryRslt
        toggle = False
        for line in fle:
            #Toggle to append next line
            if toggle == True:
                queryRslt[-1].append(line)
                #Set the toggle to false so that the next line isnt added
                toggle = False

            # If it exists in file as an idiom, append the phrase to 
            # the list (without the ending!)
            if line.lower().find(query) != -1 and line[-3] == ":":
                if line[0:-3] not in ignoreLst:
                    queryRslt.append([line[0:-3]])
                    #Set toggle to true to append the next line
                    toggle = True

        # If the search was successful, add the search to Saved data
        if len(queryRslt) > 1 and len(queryRslt) < 100:
            self.addToHistory(query)

        #Add the results to the result screen
        self.stringResults(queryRslt)

    def stringResults(self, res):
        '''
        Return a scrollable set of search results to be
        displayed in the app.
        '''
        # If there are less than one, or more than 50 results for a search,
        # return an error (as a label)
        if len(res) < 1:
            noResults = Label(id="noResults", text="[color=000000][b]Sorry, your search turned up no results.[/b][/color]", markup=True, size_hint_y=None,\
                pos_hint={'center_x':.5, 'center_y':.5})
            self.screens["menu"].ids.search.add_widget(noResults)
        elif len(res) > 100:
            tooManyResults = Label(id="tooManyResults", text="[b][color=000000]The search returned too many results![/b]", markup=True, size_hint_y=None,\
                pos_hint={'center_x':.5, 'center_y':.45})
            nexLine = Label(id="tooManyResults", text="[b][color=000000]Try adding another letter to narrow your search[/b]", markup=True, size_hint_y=None,\
                pos_hint={'center_x':.5, 'center_y':.4})
            self.screens["menu"].ids.search.add_widget(tooManyResults)
            self.screens["menu"].ids.search.add_widget(nexLine)
        # Return a series of buttons in a scrollable list. 
        else:
            gridlayout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            #Make sure the height is such that there is something to scroll.
            gridlayout.bind(minimum_height=gridlayout.setter('height'))
            
            # Create a button for each item in the list; add it to GridLayout
            num = 0
            
            # expectedHeight and gridPos will be used to position the backing canvas
            expectedHeight = len(res) * 110
            gridPos = 110
            for item in res:
                # Create gridLayout to add text to.
                nestgridlayout = GridLayout(cols=1, spacing=5, size_hint_y=None)
                with nestgridlayout.canvas:
                    Color(0, 0.55, 0.55, 1)
                    Rectangle(size=(600, 100), pos=(0, expectedHeight-gridPos))

                #increment the gridSize by the size of the search result
                gridPos += 110

                # Create labels for phrase and def'n. Add widgets to boxLayout
                phraseLabel = Label(text=item[0], size_hint_y=None, height=40)
                nestgridlayout.add_widget(phraseLabel)
                
                defLabel =  Label(text=item[1], size_hint_y=None, height=40)
                nestgridlayout.add_widget(defLabel)

                box = BoxLayout()
                # Create favorite button, ignore button. Add to boxLayout
                faveId = 'fave' + str(num)
                faveButton = ToggleButton(name=str(faveId), text='Favorite', size_hint=(.4, 1))
                faveButton.bind(on_release = partial(self.addToFavorites, item))
                
                ignoreId = 'ignore' + str(num)
                ignoreButton = Button(name=str(ignoreId), text='Ignore', size_hint=(.4, 1))
                ignoreButton.bind(on_release = partial(self.addToIgnore, item))

                box.add_widget(faveButton)
                box.add_widget(ignoreButton)
                nestgridlayout.add_widget(box)

                gridlayout.add_widget(nestgridlayout)

                num += 1

            # Create Scrollable widget, add grid layout
            scroll = ScrollView(id='scroll', size_hint=(None, None), size=(600, 200), \
                pos_hint={'center_x':.5, 'center_y':.45})

            scroll.add_widget(gridlayout)

            # Add the scrollable widget to the results page.
            self.screens["menu"].ids.search.add_widget(scroll)

    def addToIgnore(self, obj, *args):
        '''
        Add obj to list of objects to ignore in future searches. change color
        of button clicked to red
        '''
        if obj not in self.ignoreList:
            self.ignoreList.append(obj)
        #self.showIgnore(self.ignoreList)


    def removeFromIgnore(self, obj):
        '''
        Remove obj from list of ignored searches
        '''
        if obj in self.ignoreList:
            self.ignoreList.remove(obj)

    def showIgnore(self, lst):
        '''
        Show list of ignored items
        '''
        for child in self.screens["settings"].ids.ignorebox.children:
            if child.id in ['scroll']:
                self.screens["settings"].ids.ignorebox.remove_widget(child)
            elif child.id in ['noResults']:
                self.screens["menu"].ids.search.remove_widget(child)

        if len(lst) < 1:
            noResults = Label(id="noResults", text="[b][color=000000]Nothing has been added to the ignore list.[/b]", markup=True, size_hint_y=None,\
                pos_hint={'center_x':.5, 'center_y':.5})
            self.screens["settings"].ids.ignorebox.add_widget(noResults)
        else:
            layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            #Make sure the height is such that there is something to scroll.
            layout.bind(minimum_height=layout.setter('height'))
            for i in lst:
                ignoreLabel = "[b][color=000000]"+i[0] + ' - ' + i[1]+"[/b]"
                item = Label(text=ignoreLabel, markup=True, size_hint_y=None, height=40)
                layout.add_widget(item)
            
            # Create ScrollView instance, add layout
            scroll = ScrollView(id='scroll', size_hint=(1, .5), \
                pos_hint={'center_x':.5, 'center_y':.45})
            scroll.add_widget(layout)

            self.screens["settings"].ids.ignorebox.add_widget(scroll)

    def addToHistory(self, obj):
        '''
        Add obj to list of objects to ignore in future searches.
        '''
        if obj not in self.historyList:
            self.historyList.append(obj)
        #self.showHistory(self.historyList)

    def showHistory(self, lst):
        '''
        Show Search history as scrollable label
        '''

        for child in self.screens["menu"].ids.history.children:
            if child.id in ['scroll']:
                self.screens["menu"].ids.history.remove_widget(child)
            elif child.id in ['noResults']:
                self.screens["menu"].ids.search.remove_widget(child)

        if len(lst) < 1:
            noResults = Label(id="noResults", text="[b][color=000000]Nothing has been searched yet.[/b]", markup=True, size_hint_y=None,\
                pos_hint={'center_x':.5, 'center_y':.5})
            self.screens["menu"].ids.history.add_widget(noResults)
        else:
            layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            #Make sure the height is such that there is something to scroll.
            layout.bind(minimum_height=layout.setter('height'))
            for i in lst:
                item = Label(text="[b][color=000000]"+i+"[/b]", markup=True, size_hint_y=None, height=40)
                layout.add_widget(item)
            scroll = ScrollView(id='scroll', size_hint=(1, .5), \
                pos_hint={'center_x':.5, 'center_y':.45})
            scroll.add_widget(layout)

            self.screens["menu"].ids.history.add_widget(scroll)

    def addToFavorites(self, obj, *args):
        '''
        Add obj to list of objeccts in favorites list for future lookups.
        '''
        if obj not in self.favoritesList:
            self.favoritesList.append(obj)
        #self.showFavorites(self.favoritesList)

    def showFavorites(self, lst):
        '''
        Show favoritesList as scrollable label
        '''
        for child in self.screens["menu"].ids.favorite.children:
            if child.id in ['scroll']:
                self.screens["menu"].ids.favorite.remove_widget(child)
            elif child.id in ['noResults']:
                self.screens["menu"].ids.search.remove_widget(child) 
        
        if len(lst) < 1:
            noResults = Label(id="noResults", text="[b][color=000000]Nothing has been added.[/b]", markup=True, size_hint_y=None,\
                pos_hint={'center_x':.5, 'center_y':.5})
            self.screens["menu"].ids.favorite.add_widget(noResults)
        else:
            layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
            #Make sure the height is such that there is something to scroll.
            layout.bind(minimum_height=layout.setter('height'))
            for i in lst:
                faveLabel = i[0] + ' - ' + i[1]
                item = Label(id='scroll', text="[b][color=000000]"+faveLabel+"[/b]", markup=True, size_hint_y=None, height=40)
                layout.add_widget(item)
            scroll = ScrollView(size_hint=(1, .5), \
                pos_hint={'center_x':.5, 'center_y':.45})
            scroll.add_widget(layout)

            self.screens["menu"].ids.favorite.add_widget(scroll)

if __name__ == '__main__':
    CSCGroupNineApp().run()