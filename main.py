import sys
import webbrowser as web
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import StringProperty
import os.path
import re
from urllib.parse import quote
from kivy.resources import resource_add_path
from voice import record_voice
from voice import get_text_from_voice
from voice import gererate_voice_data
from voice import play_wav
import asyncio

if hasattr(sys, "_MEIPASS"):
    resource_add_path(sys._MEIPASS)
    
class AskQuestionScreen(BoxLayout, Screen):
    answer_message = StringProperty()
    press_count = 0
    def __init__(self, **kwargs):
        super(AskQuestionScreen, self).__init__(**kwargs)
        self.answer_message = ''
        self.press_count = 0
        pass

    def select_yes(self):
        if self.press_count == 1:
            self.answer_message = '既に感想を送ってくれたみたいだよ。\nありがとう！'
            return
        self.answer_message = 'ありがとう！\nこれからももっと使ってね！'
        self.press_count += 1

    def select_no(self):
        if self.press_count == 1:
            self.answer_message = '既に感想を送ってくれたみたいだよ。\nありがとうね〜'
            return
        self.answer_message = 'そうなのか…ごめんね(´・ω・｀)\nこれからもっと頑張るね(´・ω・｀)'
        self.press_count += 1


class InputKeywordScreen(BoxLayout, Screen):
    input_word = ObjectProperty(None)
    result_msg = StringProperty()
    address_to_kotobank = StringProperty("https://kotobank.jp")
    URL_message = StringProperty("コトバンクへ")
    def __init__(self, **kwargs):
        super(InputKeywordScreen, self).__init__(**kwargs)
        self.result_msg = 'ここに意味が表示されるよ'

    def get_input_msg(self):
        return self.input_word

    def get_data_from_kotobank(self):
        try:
            commands = "curl -kI https://kotobank.jp/word/" + quote(self.input_word.text) + " -o header"
            req = os.system(commands)
            f = open('header')
            header_info = f.read()  # ファイル終端まで全て読んだデータを返す
            # print(tmp)
            hit_list = re.findall("Location:.*", header_info)
            
            URL = "https://kotobank.jp"  + hit_list[0][10:]
            commands = "curl -k " + URL + " > raw.html"
            req = os.system(commands)
            f = open('raw.html')
            raw_html = f.read()  # ファイル終端まで全て読んだデータを返す
            commands = "rm -f header raw.html"
            req = os.system(commands)
        except ValueError:
            URL = raw_html = "ValueEror"
            print('ValueError')
        except KeyError:
            URL = raw_html = "KeyError"
            print("KeyError")
        except TypeError:
            URL = raw_html = "TypeError"
            print("TypeError")
        except IndexError:
            URL = raw_html = "IndexError"
            print("IndexError")
        return raw_html, URL
        
    def normalize_html(self, raw_html):
        raw_html = raw_html.replace("\n", "")
        raw_html = raw_html.replace(" ", "")
        html = raw_html.replace("\t", "")
        return html

    def shape_from_html(self, html):
        try:
            hit_list = re.search("<sectionclass=\"description\">.*</section></div><!--/.ex解説--><pclass=\"source\">", html)
            hit_data_from_html = hit_list.group()
            cut_end_point = hit_data_from_html.find('</section>')
            hit_data_from_html = hit_data_from_html[:cut_end_point]
            hit_data_from_html = re.sub("<[^>]*?>", "", hit_data_from_html)
        except ValueError:
            hit_data_from_html = "ValueEror"
            print('ValueError')
        except KeyError:
            hit_data_from_html = "KeyError"
            print("KeyError")
        except TypeError:
            hit_data_from_html = "TypeError"
            print("TypeError")
        except IndexError:
            hit_data_from_html = "IndexError"
            print("IndexError")
        except AttributeError:
            hit_data_from_html = "AttributeError"
            print("AttributeError")
        return hit_data_from_html

    def shape_result(self, hit_data_from_html):
        CHAR_MAX_NUM = 250
        CHAR_NUM_IN_LINE = 31
        cut_data = hit_data_from_html[:CHAR_MAX_NUM]
        #print("a:", cut_data)

        shaped_result = '\n'
        for i in range(int(len(cut_data)/CHAR_NUM_IN_LINE)+1):
            shaped_result += cut_data[CHAR_NUM_IN_LINE*i : CHAR_NUM_IN_LINE*i+CHAR_NUM_IN_LINE] + '\n'
            pass
        #print(len(cut_data))
        if len(cut_data) == CHAR_MAX_NUM:
            shaped_result = shaped_result[:-1] + '…\n'
        # print(b)
        return shaped_result

    def set_sent_from_text(self):
        if self.input_word.text == "":
            self.result_msg = "なにか入力してよ〜〜"
            self.address_to_kotobank = "https://kotobank.jp"
            self.URL_message = 'コトバンクへ'
            return

        raw_html, URL = self.get_data_from_kotobank()
        if (raw_html == "IndexError"):
            self.result_msg = "ごめんね、単語が見つからなかったよ"
            self.address_to_kotobank = "https://kotobank.jp"
            self.URL_message = 'コトバンクへ'
            return
        html = self.normalize_html(raw_html)
        hit_data_from_html = self.shape_from_html(html)
        if (hit_data_from_html == "AttributeError"):
            self.result_msg = "ちょっと下のボタンで検索してみて"
            self.address_to_kotobank = URL
            self.URL_message = 'この単語をコトバンクで調べよう'
            return
        msg = self.shape_result(hit_data_from_html)

        # print(msg)
        self.result_msg = msg
        self.address_to_kotobank = URL
        self.URL_message = 'この単語をコトバンクで調べよう'
        #print(self.URL_message)
        #print(self.result_msg)
        gererate_voice_data("\"" + self.result_msg + "\"", "res.wav")
        play_wav("res.wav")
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.pass_msg())
        pass

    def set_sent_from_voice(self):
        print("音声入力中")
        record_voice()
        voice_text = get_text_from_voice().replace("、", "").replace("。", "")
        # self.result_msg = "終わり"
        print("音声入力終了")
        self.input_word.text = voice_text
        self.set_sent_from_text()
        
    def access_to_kotobank(self):
        browser = web.get('"/usr/bin/google-chrome" %s')
        browser.open(self.address_to_kotobank)

class TellMeApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(InputKeywordScreen(name='input'))
        sm.add_widget(AskQuestionScreen(name='question'))
        return sm

if __name__ == '__main__':
    TellMeApp().run()


