from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from datetime import datetime
import jdatetime

class DigitalClockApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)

        self.time_label = Label(text="Time", font_size=48)
        self.date_label = Label(text="Persian Date", font_size=24)
        self.add_widget(self.time_label)
        self.add_widget(self.date_label)

        # Reminder Inputs
        reminder_box = BoxLayout(orientation='vertical', size_hint=(1, 0.3), spacing=10)

        row1 = BoxLayout(orientation='horizontal', size_hint=(1, 0.3))
        self.reminder_time_input = TextInput(hint_text="HH:MM", multiline=False, size_hint=(0.3, 1))
        self.reminder_text_input = TextInput(hint_text="Reminder message", multiline=False, size_hint=(0.5, 1))
        self.reminder_add_button = Button(text="Add Reminder", size_hint=(0.2, 1))
        self.reminder_add_button.bind(on_press=self.add_reminder)
        row1.add_widget(self.reminder_time_input)
        row1.add_widget(self.reminder_text_input)
        row1.add_widget(self.reminder_add_button)

        row2 = GridLayout(cols=7, size_hint=(1, 0.7))
        self.days_checkboxes = {}
        self.days_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in self.days_names:
            box = BoxLayout(orientation='vertical')
            label = Label(text=day, size_hint=(1, 0.5))
            cb = CheckBox(size_hint=(1, 0.5))
            self.days_checkboxes[day] = cb
            box.add_widget(label)
            box.add_widget(cb)
            row2.add_widget(box)

        reminder_box.add_widget(row1)
        reminder_box.add_widget(row2)
        self.add_widget(reminder_box)

        self.reminders = []  # Format: (time_str, message, [list_of_days])

        Clock.schedule_interval(self.update_clock, 1)

    def update_clock(self, *args):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.time_label.text = f"Time {current_time}"

        j_now = jdatetime.datetime.now()
        self.date_label.text = f"Date {j_now.strftime('%Y/%m/%d')}"

        now_time = now.strftime("%H:%M")
        today = now.strftime("%a")  # Mon, Tue, ...

        # Check Reminders
        for reminder in self.reminders:
            r_time, message, days = reminder
            if r_time == now_time and today in days:
                self.show_popup("Reminder", f"🔔 {message}")

    def add_reminder(self, instance):
        time_str = self.reminder_time_input.text.strip()
        message = self.reminder_text_input.text.strip()
        selected_days = [day for day, cb in self.days_checkboxes.items() if cb.active]

        if not self.validate_time_format(time_str):
            self.show_popup("Invalid Time", "Please enter time in HH:MM format.")
            return

        if not message:
            self.show_popup("No Message", "Please enter a reminder message.")
            return

        if not selected_days:
            self.show_popup("No Days", "Please select at least one day.")
            return

        self.reminders.append((time_str, message, selected_days))
        self.reminder_time_input.text = ""
        self.reminder_text_input.text = ""
        for cb in self.days_checkboxes.values():
            cb.active = False

        self.show_popup("Reminder Added", f"{message} set for {time_str} on {', '.join(selected_days)}")

    def validate_time_format(self, time_str):
        if len(time_str) == 5 and time_str[2] == ":":
            hh, mm = time_str.split(":")
            if hh.isdigit() and mm.isdigit():
                h = int(hh)
                m = int(mm)
                return 0 <= h < 24 and 0 <= m < 60
        return False

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(0.6, 0.4))
        popup.open()

class ClockApp(App):
    def build(self):
        return DigitalClockApp()

if __name__ == '__main__':
    ClockApp().run()
