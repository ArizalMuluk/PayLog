from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition, NoTransition
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.clock import Clock

Window.size = (350, 600)

class BaseScreen(MDScreen):
    pass

class Cart(MDScreen):
    pass

class AddMenu(MDScreen):
    pass

class History(MDScreen):
    pass

class Settings(MDScreen):
    pass

class MainApp(MDApp):
    root: MDBoxLayout | None = None
    current_active = StringProperty("Add Menu")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = 'Red'
    
    def on_start(self):
        if self.root:
            screen_manager = self.root.ids.get('screen_manager')
            if screen_manager:
                screen_manager.current = 'Add Menu'
            else:
                print(f"[ERROR]: Screen manager dengan id {screen_manager} tidak ditemukan.")
                
    def switch_screen(self, screen_name):
        if not self.root:
            return
            
        self.current_active = screen_name
        screen_manager = self.root.ids.get('screen_manager')
        
        if screen_manager:
            if screen_manager.current == screen_name:
                return
                
            try:
                current_screen_name = screen_manager.current
                screen_names_list = screen_manager.screen_names
                
                if not current_screen_name or current_screen_name not in screen_names_list:
                    screen_manager.transition = SlideTransition(direction='left')
                    screen_manager.current = screen_name
                    return
                
                current_idx = screen_names_list.index(current_screen_name)
                target_idx = screen_names_list.index(screen_name)
                
                direction = ''
                if target_idx > current_idx:
                    direction = 'left'
                elif target_idx < current_idx:
                    direction = 'right'
                else:
                    screen_manager.transition = NoTransition()
                    screen_manager.current = screen_name
                    return
                
                screen_manager.transition = SlideTransition(direction=direction, duration=0.2)
                screen_manager.current = screen_name

            except Exception as e:
                print(f"[ERROR]: {e}. Menggunakan NoTransition.")
                screen_manager.transition = NoTransition()
                screen_manager.current = screen_name
        else:
            print(f"[ERROR]: Screen manager dengan id 'screen_manager' tidak ditemukan.")
    
    def build(self):
        self.theme_cls.theme_style = "Dark"  # Ensure light theme
        return super().build()

if __name__ == '__main__':
    MainApp().run()