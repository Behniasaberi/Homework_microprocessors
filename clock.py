from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse

from datetime import datetime
import pytz
import jdatetime
import pyttsx3
import random
import json
import os
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
            Color(0.15, 0.15, 0.2)
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius * 2, radius * 2))

            # ساعت‌ها (12 نشانگر)
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

            # عقربه ساعت
            hour_angle = radians(30 * hour)
            Color(1, 0, 0)
            Line(points=[center_x, center_y,
                         center_x + 0.4 * radius * sin(hour_angle),
                         center_y + 0.4 * radius * cos(hour_angle)], width=4)

            # عقربه دقیقه
            minute_angle = radians(6 * min_)
            Color(0, 1, 0)
            Line(points=[center_x, center_y,
                         center_x + 0.6 * radius * sin(minute_angle),
                         center_y + 0.6 * radius * cos(minute_angle)], width=3)

            # عقربه ثانیه
            second_angle = radians(6 * sec)
            Color(0.3, 0.6, 1)
            Line(points=[center_x, center_y,
                         center_x + 0.75 * radius * sin(second_angle),
                         center_y + 0.75 * radius * cos(second_angle)], width=2)

            Color(1, 1, 0)
            Ellipse(pos=(center_x - 5, center_y - 5), size=(10, 10))


class ClockTabs(TabbedPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.do_default_tab = False
        self.selected_timezone = "Asia/Tehran"
        self.reminders = []
        self.reminder_file = "reminders.json"
        self.load_reminders()

        self.motivational_quotes = [
            "Keep going, you're doing great!",
            "Believe in yourself and all that you are.",
            "Success is the sum of small efforts repeated daily.",
            "Stay positive, work hard, make it happen.",
            "Your only limit is your mind."
        ]

        self.continent_city_map = {
            "Asia": {"Tehran": "Asia/Tehran", "Tokyo": "Asia/Tokyo", "Dubai": "Asia/Dubai"},
            "Europe": {"London": "Europe/London", "Berlin": "Europe/Berlin", "Moscow": "Europe/Moscow"},
            "America": {"New York": "America/New_York", "Los Angeles": "America/Los_Angeles", "Sao Paulo": "America/Sao_Paulo"},
            "Africa": {"Cairo": "Africa/Cairo", "Lagos": "Africa/Lagos", "Johannesburg": "Africa/Johannesburg"},
            "Australia": {"Sydney": "Australia/Sydney", "Melbourne": "Australia/Melbourne", "Perth": "Australia/Perth"}
        }

        self.digital_tab = self.create_digital_tab()
        self.analog_tab = self.create_analog_tab()  # تب آنالوگ
        self.reminder_tab = self.create_reminder_tab()

        self.add_widget(self.digital_tab)
        self.add_widget(self.analog_tab)
        self.add_widget(self.reminder_tab)

        Clock.schedule_interval(self.update_clock, 1)

    def create_digital_tab(self):
        tab = TabbedPanelItem(text='🕓 Digital')
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.time_label = Label(text='--:--:--', font_size=48)
        self.date_label = Label(text='----/--/--', font_size=24)
        self.quote_label = Label(text='', font_size=18, halign='center', valign='middle')
        self.quote_label.bind(size=self.quote_label.setter('text_size'))

        self.continent_spinner = Spinner(text='Select Continent', values=list(self.continent_city_map.keys()), size_hint=(1, 0.2))
        self.continent_spinner.bind(text=self.on_continent_select)
        self.city_spinner = Spinner(text='Select City', values=[], size_hint=(1, 0.2))
        self.city_spinner.bind(text=self.on_city_select)

        self.speak_button = Button(text="🗣️ Say Time", size_hint=(1, 0.2))
        self.speak_button.bind(on_press=self.speak_current_time)

        layout.add_widget(self.time_label)
        layout.add_widget(self.date_label)
        layout.add_widget(self.quote_label)
        layout.add_widget(self.continent_spinner)
        layout.add_widget(self.city_spinner)
        layout.add_widget(self.speak_button)

        tab.add_widget(layout)
        return tab

    def create_analog_tab(self):
        tab = TabbedPanelItem(text='⏰ Analog')
        clock = AnalogClock()
        tab.add_widget(clock)
        return tab

    def create_reminder_tab(self):
        tab = TabbedPanelItem(text='🔔 Reminders')
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        row1 = BoxLayout(size_hint=(1, 0.3))
        self.reminder_time_input = TextInput(hint_text='HH:MM', size_hint=(0.3, 1))
        self.reminder_text_input = TextInput(hint_text='Message', size_hint=(0.5, 1))
        add_btn = Button(text='Add', size_hint=(0.2, 1))
        add_btn.bind(on_press=self.add_reminder)
        row1.add_widget(self.reminder_time_input)
        row1.add_widget(self.reminder_text_input)
        row1.add_widget(add_btn)

        row2 = GridLayout(cols=7, size_hint=(1, 0.7))
        self.days_checkboxes = {}
        for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
            col = BoxLayout(orientation='vertical')
            label = Label(text=day)
            cb = CheckBox()
            self.days_checkboxes[day] = cb
            col.add_widget(label)
            col.add_widget(cb)
            row2.add_widget(col)

        layout.add_widget(row1)
        layout.add_widget(row2)
        tab.add_widget(layout)
        return tab

    def on_continent_select(self, spinner, continent):
        cities = list(self.continent_city_map[continent].keys())
        self.city_spinner.values = cities
        self.city_spinner.text = 'Select City'

    def on_city_select(self, spinner, city):
        continent = self.continent_spinner.text
        if continent in self.continent_city_map and city in self.continent_city_map[continent]:
            self.selected_timezone = self.continent_city_map[continent][city]

    def update_clock(self, *args):
        try:
            tz = pytz.timezone(self.selected_timezone)
            now = datetime.now(tz)
            self.time_label.text = now.strftime('%H:%M:%S')
            j_now = jdatetime.datetime.fromgregorian(datetime=now)
            self.date_label.text = j_now.strftime('%Y/%m/%d')

            # Update motivational quote every full hour
            if now.minute == 0 and now.second == 0:
                self.quote_label.text = random.choice(self.motivational_quotes)

            now_time = now.strftime("%H:%M")
            today = now.strftime("%a")
            for r_time, message, days in self.reminders:
                if r_time == now_time and today in days:
                    self.show_popup("Reminder", f"🔔 {message}")
        except:
            self.time_label.text = "--:--:--"
            self.date_label.text = "Invalid timezone"

    def speak_current_time(self, instance):
        try:
            tz = pytz.timezone(self.selected_timezone)
            now = datetime.now(tz)
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(f"The time is {now.strftime('%H')} and {now.strftime('%M')} minutes")
            engine.runAndWait()
        except:
            self.show_popup("Error", "Failed to speak time")

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
        self.save_reminders()

        self.reminder_time_input.text = ""
        self.reminder_text_input.text = ""
        for cb in self.days_checkboxes.values():
            cb.active = False

        self.show_popup("Reminder Added", f"{message} set for {time_str} on {', '.join(selected_days)}")

    def validate_time_format(self, time_str):
        if len(time_str) == 5 and time_str[2] == ":":
            hh, mm = time_str.split(":")
            return hh.isdigit() and mm.isdigit() and 0 <= int(hh) < 24 and 0 <= int(mm) < 60
        return False

    def show_popup(self, title, msg):
        popup = Popup(title=title, content=Label(text=msg), size_hint=(0.6, 0.4))
        popup.open()

    def save_reminders(self):
        try:
            with open(self.reminder_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False)
        except:
            self.show_popup("Error", "Failed to save reminders.")

    def load_reminders(self):
        if os.path.exists(self.reminder_file):
            try:
                with open(self.reminder_file, 'r', encoding='utf-8') as f:
                    self.reminders = json.load(f)
            except:
                self.reminders = []


class WorldClockApp(App):
    def build(self):
        return ClockTabs()


if __name__ == '__main__':
    WorldClockApp().run()
