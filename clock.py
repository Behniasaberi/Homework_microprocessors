from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.core.audio import SoundLoader
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from datetime import datetime
import jdatetime
import pytz
import pyttsx3
from math import sin, cos, radians


class AnalogClock(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        self.canvas.clear()
        with self.canvas:
            center_x, center_y = self.center
            radius = min(self.width, self.height) * 0.45

            # ⏺️ Draw background
            Color(0.15, 0.15, 0.2)  # dark background
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

            # ⏱️ Tick marks
            for i in range(12):
                angle_deg = 30 * i
                angle_rad = radians(angle_deg)
                start_x = center_x + 0.85 * radius * sin(angle_rad)
                start_y = center_y + 0.85 * radius * cos(angle_rad)
                end_x = center_x + radius * sin(angle_rad)
                end_y = center_y + radius * cos(angle_rad)
                Color(1, 1, 1)
                Line(points=[start_x, start_y, end_x, end_y], width=2)

            now = datetime.now()
            sec = now.second
            min_ = now.minute
            hour = now.hour % 12 + min_ / 60.0

            # 🟥 Hour hand
            hour_angle = radians(30 * hour)
            Color(1, 0, 0)
            Line(points=[center_x, center_y,
                         center_x + 0.4 * radius * sin(hour_angle),
                         center_y + 0.4 * radius * cos(hour_angle)], width=4)

            # 🟩 Minute hand
            minute_angle = radians(6 * min_)
            Color(0, 1, 0)
            Line(points=[center_x, center_y,
                         center_x + 0.6 * radius * sin(minute_angle),
                         center_y + 0.6 * radius * cos(minute_angle)], width=3)

            # 🔵 Second hand
            second_angle = radians(6 * sec)
            Color(0.3, 0.6, 1)
            Line(points=[center_x, center_y,
                         center_x + 0.75 * radius * sin(second_angle),
                         center_y + 0.75 * radius * cos(second_angle)], width=2)

            # ⚫ Center Dot
            Color(1, 1, 0)
            Ellipse(pos=(center_x - 5, center_y - 5), size=(10, 10))


class DigitalClockApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)

        # ⏱️ Analog & Digital Switch Button
        self.clock_mode = "digital"  # or "analog"
        self.switch_btn = Button(text="🔁 Switch to Analog", size_hint=(1, 0.1))
        self.switch_btn.bind(on_press=self.switch_clock)
        self.add_widget(self.switch_btn)

        # ⏰ Analog clock widget
        self.analog_clock = AnalogClock(size_hint=(1, 0.5))
        self.analog_clock.opacity = 0  # hidden by default

        # ⏲️ Digital clock labels
        self.time_label = Label(text="Time", font_size=48)
        self.date_label = Label(text="Persian Date", font_size=24)

        self.add_widget(self.analog_clock)
        self.add_widget(self.time_label)
        self.add_widget(self.date_label)

        self.speak_button = Button(text="🗣️ Say Time", size_hint=(1, 0.1))
        self.speak_button.bind(on_press=lambda x: self.speak_current_time())
        self.add_widget(self.speak_button)

        self.world_clocks = {
            "Tehran": ("Asia/Tehran", Label(font_size=18)),
            "New York": ("America/New_York", Label(font_size=18)),
            "London": ("Europe/London", Label(font_size=18)),
            "Tokyo": ("Asia/Tokyo", Label(font_size=18))
        }

        world_box = BoxLayout(orientation='vertical', size_hint=(1, 0.3))
        for city, (_, label) in self.world_clocks.items():
            label.text = f"{city}: --:--"
            world_box.add_widget(label)
        self.add_widget(world_box)

        # ⏰ Reminder setup
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
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
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

        self.reminders = []
        self.sound = SoundLoader.load('alarm.mp3')

        Clock.schedule_interval(self.update_clock, 1)

    def switch_clock(self, instance):
        if self.clock_mode == "digital":
            self.clock_mode = "analog"
            self.analog_clock.opacity = 1
            self.time_label.opacity = 0
            self.date_label.opacity = 0
            self.switch_btn.text = "🔁 Switch to Digital"
        else:
            self.clock_mode = "digital"
            self.analog_clock.opacity = 0
            self.time_label.opacity = 1
            self.date_label.opacity = 1
            self.switch_btn.text = "🔁 Switch to Analog"

    def update_clock(self, *args):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.time_label.text = f"Time {current_time}"

        j_now = jdatetime.datetime.now()
        self.date_label.text = f"Date {j_now.strftime('%Y/%m/%d')}"

        for city, (tz_name, label) in self.world_clocks.items():
            tz = pytz.timezone(tz_name)
            local_time = datetime.now(tz).strftime("%H:%M:%S")
            label.text = f"{city}: {local_time}"

        now_time = now.strftime("%H:%M")
        today = now.strftime("%a")
        for r_time, message, days in self.reminders:
            if r_time == now_time and today in days:
                self.play_alarm()
                self.show_popup("Reminder", f"🔔 {message}")

    def speak_current_time(self):
        now = datetime.now()
        hour = now.strftime("%H")
        minute = now.strftime("%M")

        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.say(f"The time is {hour} and {minute} minutes.")
        engine.runAndWait()

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

    def play_alarm(self):
        if self.sound:
            self.sound.stop()
            self.sound.play()


class ClockApp(App):
    def build(self):
        return DigitalClockApp()


if __name__ == '__main__':
    ClockApp().run()
