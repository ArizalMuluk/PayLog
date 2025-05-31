from kivymd.app import MDApp
from kivy.uix.screenmanager import SlideTransition, NoTransition
from kivy.properties import StringProperty, NumericProperty
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window
from kivy.uix.image import Image as KivyImage
from kivy.animation import Animation
from kivy.metrics import dp

from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDIconButton
import os
import db_manager

Window.size = (350, 600)

class BaseScreen(MDScreen):
    pass

class CartListItem(MDBoxLayout):
    item_name = StringProperty()
    item_price = NumericProperty()
    item_quantity = NumericProperty()
    item_image_path = StringProperty()

    def __init__(self, item_data, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.adaptive_height = True
        self.spacing = dp(10)
        self.padding = dp(8)

        self.item_name = item_data['name']
        self.item_price = item_data['price']
        self.item_quantity = item_data['quantity']
        self.item_image_path = item_data.get('image_path', "images/placeholder.png")

        actual_display_image_path = self.item_image_path
        if not (self.item_image_path and os.path.exists(self.item_image_path)):
            placeholder = "images/placeholder.png"
            if os.path.exists(placeholder):
                actual_display_image_path = placeholder
            else:
                actual_display_image_path = ""

        img = FitImage(
            source=actual_display_image_path,
            size_hint=(None, None),
            size=(dp(56), dp(56)),
            radius=[dp(4)],
            mipmap=True
        )
        self.add_widget(img)

        info_box = MDBoxLayout(orientation='vertical', adaptive_height=True, size_hint_x=0.5, spacing=dp(4))
        info_box.add_widget(MDLabel(text=self.item_name, font_style="Subtitle1", adaptive_height=True, shorten=True, shorten_from='right'))
        info_box.add_widget(MDLabel(text=f"Rp {self.item_price:,.0f}".replace(",", "."), theme_text_color="Secondary", adaptive_height=True))
        self.add_widget(info_box)

        qty_box = MDBoxLayout(orientation='horizontal', adaptive_width=True, size_hint_x=None, spacing=dp(1), pos_hint={'center_y': 0.5})
        btn_decrement = MDIconButton(icon="minus-circle-outline", on_release=self.decrement_quantity, icon_size="22sp", theme_text_color="Secondary")
        self.qty_label = MDLabel(text=str(self.item_quantity), halign="center", size_hint_x=None, width=dp(28), adaptive_height=True, theme_text_color="Primary", bold=True)
        btn_increment = MDIconButton(icon="plus-circle-outline", on_release=self.increment_quantity, icon_size="22sp", theme_text_color="Primary")
        qty_box.add_widget(btn_decrement)
        qty_box.add_widget(self.qty_label)
        qty_box.add_widget(btn_increment)
        self.add_widget(qty_box)

        subtotal = self.item_price * self.item_quantity
        self.add_widget(MDLabel(text=f"Rp {subtotal:,.0f}".replace(",", "."), size_hint_x=0.3, halign="right", adaptive_height=True, font_style="Subtitle2", pos_hint={'center_y': 0.5}))

    def increment_quantity(self, *args):
        app = MDApp.get_running_app()
        if app:
            app.update_cart_item_quantity(self.item_name, 1)
        else:
            print(f"[ERROR]: Aplikasi tidak ditemukan.")

    def decrement_quantity(self, *args):
        app = MDApp.get_running_app()
        if app:
            app.update_cart_item_quantity(self.item_name, -1)
        else:
            print(f"[ERROR]: Aplikasi tidak ditemukan.")

class Cart(MDScreen):
    def on_enter(self):
        self.update_cart_display()

    def update_cart_display(self):
        app = MDApp.get_running_app()
        if not app or not hasattr(self, 'ids') or 'cart_items_list' not in self.ids:
            return

        cart_list_widget = self.ids.cart_items_list
        cart_list_widget.clear_widgets()
        cart_items_data = app.get_cart_items_list()

        if not cart_items_data:
            cart_list_widget.add_widget(
                MDLabel(
                    text="Keranjang Anda kosong.", halign="center",
                    theme_text_color="Secondary", padding_y=dp(20),
                    font_style="Subtitle1"
                )
            )
        else:
            for item_data in cart_items_data:
                cart_item_view = CartListItem(item_data=item_data)
                cart_list_widget.add_widget(cart_item_view)

        total_price = app.get_cart_total()
        if hasattr(self, 'ids') and 'total_price_label' in self.ids:
            self.ids.total_price_label.text = f"Total: Rp {total_price:,.0f}".replace(",", ".")

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
        elif os.path.exists(placeholder):
            self.actual_image_source = placeholder
        else:
            self.actual_image_source = ""

    def add_item_to_cart(self):
        app = MDApp.get_running_app()
        if not app:
            return

        app.add_item_to_app_cart(self)

        try:
            if not self.actual_image_source:
                return

            source_visual_element = self.ids.product_image_in_card
            if not source_visual_element:
                return

            start_pos_abs = source_visual_element.to_window(*source_visual_element.center)

            cart_icon_widget = app.root.ids.get('cart_nav_icon_target')
            if not cart_icon_widget:
                return

            target_pos_abs = cart_icon_widget.to_window(*cart_icon_widget.center)

            anim_item = KivyImage(
                source=self.actual_image_source,
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                allow_stretch=True,
                keep_ratio=True,
                mipmap=True
            )
            anim_item.center_x = start_pos_abs[0]
            anim_item.center_y = start_pos_abs[1]

            Window.add_widget(anim_item)

            duration = 0.5
            anim = Animation(
                center_x=target_pos_abs[0],
                center_y=target_pos_abs[1],
                size=(dp(10), dp(10)),
                opacity=0.3,
                t='out_quad',
                duration=duration
            )

            def on_animation_finish(animation, widget_animated):
                Window.remove_widget(widget_animated)

            anim.bind(on_complete=on_animation_finish)
            anim.start(anim_item)

        except Exception as e:
            print(f"Animasi gagal: {e}")


class AddItemDialogContent(MDBoxLayout):
    file_manager = None
    manager_open = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(12)
        self.size_hint_y = None
        self.height = self.minimum_height
        self.padding = [dp(16), dp(12), dp(16), dp(24)]

        self.name_field = MDTextField(hint_text="Nama Menu", mode="fill", required=True)

        image_input_layout = MDBoxLayout(orientation='horizontal', adaptive_height=True, spacing=dp(10))
        self.image_path_display = MDTextField(
            hint_text="Pilih Gambar Menu",
            mode="fill",
            readonly=True,
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
        if AddItemDialogContent.manager_open:
            return

        from kivy.utils import platform
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission #type: ignore
                request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            except ImportError:
                pass

        path = os.path.expanduser("~")
        AddItemDialogContent.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
            ext=['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        )
        AddItemDialogContent.file_manager.show(path)
        AddItemDialogContent.manager_open = True

    def select_path(self, path: str):
        self.image_path_display.text = path
        self.exit_manager()

    def exit_manager(self, *args):
        if AddItemDialogContent.file_manager:
            AddItemDialogContent.file_manager.close()
        AddItemDialogContent.manager_open = False

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
            content = AddItemDialogContent()
            self.dialog = MDDialog(
                title="Tambah Menu Baru",
                type="custom",
                content_cls=content,
                buttons=[
                    MDFlatButton(
                        text="BATAL",
                        on_release=self.dismiss_dialog
                    ),
                    MDRaisedButton(
                        text="TAMBAH",
                        on_release=self.submit_new_item_from_dialog
                    ),
                ],
            )
        dialog_actual_content = self.dialog.content_cls

        dialog_actual_content.name_field.text = ""
        dialog_actual_content.image_path_display.text = ""
        dialog_actual_content.price_field.text = ""
        dialog_actual_content.name_field.error = False
        dialog_actual_content.price_field.error = False
        self.dialog.open()

    def dismiss_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def submit_new_item_from_dialog(self, *args):
        if not self.dialog:
            print("Error: Dialog tidak ditemukan di submit_new_item_from_dialog")
            return

        content = self.dialog.content_cls

        name = content.name_field.text
        image_path = content.image_path_display.text
        price_text = content.price_field.text

        content.name_field.error = False
        content.price_field.error = False

        if not name or not price_text:
            if not name: content.name_field.error = True
            if not price_text: content.price_field.error = True
            return

        try:
            price = float(price_text)
            db_manager.add_menu_item(name, image_path, price)
            self.load_items_from_db()

            current_search_text = self.ids.get('search_field').text if self.ids.get('search_field') else ""
            if current_search_text:
                self.search_items(current_search_text)
            else:
                self.display_all_items()

            if self.dialog:
                self.dialog.dismiss()
        except ValueError:
            content.price_field.error = True
        except Exception as e:
            print(f"Gagal menambahkan item: {e}")

class History(MDScreen):
    pass

class Settings(MDScreen):
    pass

class MainApp(MDApp):
    root = None
    current_active = StringProperty("Add Menu")
    cart_items = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.primary_palette = 'Red'
        self.cart_items = {}

    def add_item_to_app_cart(self, menu_card_instance):
        item_name = menu_card_instance.name
        item_price = menu_card_instance.price
        item_image = menu_card_instance.actual_image_source

        if item_name in self.cart_items:
            self.cart_items[item_name]['quantity'] += 1
        else:
            self.cart_items[item_name] = {
                'name': item_name,
                'price': item_price,
                'quantity': 1,
                'image_path': item_image
            }
        if self.root and self.root.ids.screen_manager.current == 'Cart':
            cart_screen = self.root.ids.screen_manager.get_screen('Cart')
            cart_screen.update_cart_display()

    def update_cart_item_quantity(self, item_name, change_amount):
        if item_name in self.cart_items:
            self.cart_items[item_name]['quantity'] += change_amount
            if self.cart_items[item_name]['quantity'] <= 0:
                del self.cart_items[item_name]

        if self.root and self.root.ids.screen_manager.current == 'Cart':
            cart_screen = self.root.ids.screen_manager.get_screen('Cart')
            cart_screen.update_cart_display()

    def get_cart_total(self):
        total = 0.0
        for item_data in self.cart_items.values():
            total += item_data['price'] * item_data['quantity']
        return total

    def get_cart_items_list(self):
        return list(self.cart_items.values())

    def on_start(self):
        db_manager.init_db()
        if self.root:
            screen_manager = self.root.ids.get('screen_manager')
            if screen_manager:
                if not screen_manager.current:
                    screen_manager.current = 'Add Menu'
            else:
                print(f"[ERROR]: Screen manager tidak ditemukan.")

    def switch_screen(self, screen_name):
        if not self.root:
            return

        screen_manager = self.root.ids.get('screen_manager')
        if not screen_manager:
            return

        if screen_manager.current == screen_name and self.current_active == screen_name :
            return

        self.current_active = screen_name

        try:
            current_screen_name = screen_manager.current
            screen_names_list = screen_manager.screen_names

            if not current_screen_name or current_screen_name not in screen_names_list:
                screen_manager.transition = NoTransition()
                screen_manager.current = screen_name
                return

            if screen_manager.current == screen_name:
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
            screen_manager.transition = NoTransition()
            screen_manager.current = screen_name

    def build(self):
        self.theme_cls.theme_style = "Light"
        return

    def events(self, window, key, *args):
        if key == 27: # Android back button
            if AddMenu.dialog and hasattr(AddMenu.dialog.content_cls, 'manager_open') and AddMenu.dialog.content_cls.manager_open:
                if hasattr(AddMenu.dialog.content_cls, 'file_manager') and AddMenu.dialog.content_cls.file_manager:
                    AddMenu.dialog.content_cls.file_manager.back()
                    return True
            elif AddMenu.dialog and AddMenu.dialog.open_button_press_time != 0:
                AddMenu.dialog.dismiss()
                return True
        return False

if __name__ == '__main__':
    MainApp().run()