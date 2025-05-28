from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivy.uix.screenmanager import SlideTransition, NoTransition
from kivy.properties import StringProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window

Window.size = (350, 600)

class NavigationItemBar(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()
    
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
    
    def on_start(self):
        if self.root:
            screen_manager = self.root.ids.get('screen_manager')
            if screen_manager:
                screen_manager.current = 'Add Menu'
            else:
                print(f"[ERROR]: Screen manager dengan id {screen_manager} tidak ditemukan.")

    def on_switch_tabs(
        self,
        bar: MDNavigationBar,
        item: MDNavigationItem,
        item_icon: str,
        item_text: str,
    ):
        if not self.root:
            return

        screen_manager = self.root.ids.get('screen_manager')
        if screen_manager:
            if screen_manager.current == item_text:
                return
            try:
                current_screen_name = screen_manager.current
                screen_names_list = screen_manager.screen_names
                
                if not current_screen_name or current_screen_name not in screen_names_list:
                    print(f"[WARNING]: Layar saat ini '{current_screen_name}' tidak ditemukan.")
                    screen_manager.transition = SlideTransition(direction='left')
                    screen_manager.current = item_text
                    return
                
                current_idx = screen_names_list.index(current_screen_name)
                target_idx = screen_names_list.index(item_text)
                
                direction = ''
                if target_idx > current_idx:
                    direction = 'left'
                elif target_idx < current_idx:
                    direction = 'right'
                else:
                    screen_manager.transition = NoTransition()
                    screen_manager.current = item_text
                    return
                
                screen_manager.transition = SlideTransition(direction=direction, duration=0.2)
                screen_manager.current = item_text

            except ValueError:
                print(f"[ERROR]: ValueError saat transisi: Current='{screen_manager.current}', Target='{item_text}'. Menggunakan NoTransition.")
                screen_manager.transition = NoTransition()
                screen_manager.current = item_text

            except Exception as e:
                print(f"[ERROR]: Terjadi kesalahan tak terduga: {e}. Menggunakan NoTransition.")
                screen_manager.transition = NoTransition()
                screen_manager.current = item_text
        else:
            print(f"[ERROR]: Screen manager dengan id 'screen_manager' tidak ditemukan.")
    
    def build(self):
        return super().build()

if __name__ == '__main__':
    MainApp().run()