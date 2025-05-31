from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition, NoTransition
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window

from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivy.metrics import dp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
import os
import db_manager

Window.size = (350, 600)

class BaseScreen(MDScreen):
    pass

class Cart(MDScreen):
    pass

class MenuCard(MDCard):
    name = StringProperty()
    image_path = StringProperty()
    price = NumericProperty()
    actual_image_source = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(image_path=self._update_actual_image_source)
        self._update_actual_image_source()

    def _update_actual_image_source(self, *args):
        placeholder = "images/placeholder.png"
        if self.image_path and os.path.exists(self.image_path):
            self.actual_image_source = self.image_path
        else:
            self.actual_image_source = placeholder

class AddItemDialogContent(MDBoxLayout):
    file_manager = None
    manager_open = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(12)
        self.size_hint_y = None
        self.height = dp(200) 
        self.padding = dp(10)

        self.name_field = MDTextField(hint_text="Nama Menu", mode="fill", required=True)
        
        image_input_layout = MDBoxLayout(orientation='horizontal', adaptive_height=True, spacing=dp(10))
        self.image_path_display = MDTextField(
            hint_text="Pilih Gambar Menu", 
            mode="fill", 
            readonly=True, 
            # helper_text="Klik ikon folder untuk memilih gambar",
            helper_text_mode = "on_focus"
        )
        self.browse_button = MDIconButton(
            icon="folder-open-outline", 
            on_release=self.open_file_manager,
            pos_hint={'center_y': 0.5}
        )
        image_input_layout.add_widget(self.image_path_display)
        image_input_layout.add_widget(self.browse_button)

        self.price_field = MDTextField(hint_text="Harga", input_filter="float", mode="fill", required=True)

        self.add_widget(self.name_field)
        self.add_widget(image_input_layout)
        self.add_widget(self.price_field)

    def open_file_manager(self, *args):
        if self.manager_open:
            return

        from kivy.utils import platform
        if platform == 'android':
            from android.permissions import request_permissions, Permission #type: ignore
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        
        path = os.path.expanduser("~")

        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
            ext=['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        )
        self.file_manager.show(path)
        self.manager_open = True

    def select_path(self, path: str):
        self.image_path_display.text = path
        self.exit_manager()

    def exit_manager(self, *args):
        if self.file_manager:
            self.file_manager.close()
        self.manager_open = False

class AddMenu(MDScreen):
    dialog = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.all_menu_items_from_db = []

    def on_enter(self):
        self.load_items_from_db()
        search_input_widget = self.ids.get('search_field')
        if search_input_widget and search_input_widget.text:
            self.search_items(search_input_widget.text)
        else:
            self.display_all_items()

    def load_items_from_db(self):
        self.all_menu_items_from_db = db_manager.get_all_menu_items()
        print(f"[SUCCESS]: Berhasil memuat {len(self.all_menu_items_from_db)} item dari database.")

    def display_all_items(self):
        if not hasattr(self, 'ids') or not self.ids:
            return
        result_list = self.ids.get('search_result_list')
        if not result_list:
            return
        
        result_list.clear_widgets()
        for item_data in self.all_menu_items_from_db:
            self._create_and_add_card(item_data, result_list)

    def search_items(self, query):
        if not hasattr(self, 'ids') or not self.ids:
            return
        
        result_list = self.ids.get('search_result_list')
        if not result_list:
            return

        result_list.clear_widgets()

        if not query:
            self.display_all_items()
            return

        for item_data in self.all_menu_items_from_db:
            if query.lower() in item_data['name'].lower():
                self._create_and_add_card(item_data, result_list)
                
    def _create_and_add_card(self, item_data, result_list_widget):
        card = MenuCard(
            name=item_data['name'],
            image_path=item_data.get('image', ''),
            price=item_data['price']
        )
        result_list_widget.add_widget(card)

    def open_add_item_dialog(self):
        if not self.dialog:
            self.dialog_content = AddItemDialogContent()
            self.dialog = MDDialog(
                title="Tambah Menu Baru",
                type="custom",
                content_cls=self.dialog_content,
                buttons=[
                    MDFlatButton(
                        text="BATAL",
                        on_release=lambda x: self.dialog.dismiss() #type: ignore
                    ),
                    MDRaisedButton(
                        text="TAMBAH",
                        on_release=lambda x: self.submit_new_item_from_dialog()
                    ),
                ],
            )
        self.dialog_content.name_field.text = ""
        self.dialog_content.image_path_display.text = ""
        self.dialog_content.price_field.text = ""
        self.dialog.open()

    def submit_new_item_from_dialog(self, *args):
        name = self.dialog_content.name_field.text
        image_path = self.dialog_content.image_path_display.text
        price_text = self.dialog_content.price_field.text

        if not name or not price_text:
            print("[WARNING]: Nama dan Harga tidak boleh kosong.")
            if not name: self.dialog_content.name_field.error = True
            if not price_text: self.dialog_content.price_field.error = True
            return

        try:
            price = float(price_text)
            db_manager.add_menu_item(name, image_path, price)
            self.load_items_from_db()
            self.display_all_items()
            if self.dialog:
                self.dialog.dismiss()
        except ValueError:
            print("[ERROR]: Harga harus berupa angka.")
            self.dialog_content.price_field.error = True
        except Exception as e:
            print(f"[ERROR]: Gagal menambahkan item dari dialog: {e}")

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
        db_manager.init_db()
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
            print(f"[ERROR]: Screen manager dengan id {screen_manager} tidak ditemukan.")
    
    def build(self):
        self.theme_cls.theme_style = "Light"
        return super().build()
    
    def events(self, window, key, *args):
        """Menangani event tombol kembali di Android untuk MDFileManager."""
        if key == 27:
            if AddMenu.dialog and AddMenu.dialog.content_cls.manager_open:
                AddMenu.dialog.content_cls.file_manager.back()
                return True
        return False

if __name__ == '__main__':
    MainApp().run()