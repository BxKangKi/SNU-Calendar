import requests as req
from bs4 import BeautifulSoup as bs
import pandas as pd
import vobject, time, os, pytz
from datetime import date, datetime

AUTHOR = "Seoul National University<@snu.ac.kr>, Kiyeon Kang<kngky078@snu.ac.kr>"
FILE_OUTPUT_PATH = "docs/calendar.ics"

def extract_digits(text):
  return [int(num) for num in text if num.isdigit()]

def join_digits(n):
  return int(''.join(map(str, n)))

# check containss
def contain(ls, txt):
  return ls.find(txt) != -1

def clamp_index(s, m, x):
    return s[min(len(s), m):min(len(s), x)]

class Date:
  def __init__(self, year, month):
    self.day = 0
    self.year = int(year)
    self.month = int(month)
  def string(self):
    return str(self.year) + "-" + str(self.month) + "-" + str(self.day)


class Content:
  def __init__(self, a, b, desc):
    self.date_a = Date(a.year, a.month)
    self.date_b = Date(b.year, b.month)
    self.desc = desc
  def print(self):
    print(self.date_a.string() + "~" + self.date_b.string() + ": " + self.desc)


def get_date(m, y): 
  digits = extract_digits(m)
  date = Date(0, 0)
  if (len(digits) < 3):
    date.month = join_digits(digits)
    date.year = int(y)
  else:
    date.year = join_digits(digits[0:4])
    date.month = join_digits(digits[4:])
  return date


def get_content(cal, soup, date):
  content = soup.select('div.work-content')
  for x in content:
    work = x.select('div.work')
    for y in work:
      desc = y.select_one('p.desc').get_text()
      c = Content(date, date, desc)
      day = y.select_one('p.day').get_text()
      digits = extract_digits(day)
      print(digits)
      if len(digits) < 3:
          c.date_a.day = join_digits(digits)
          c.date_b.day = join_digits(digits)
      elif len(digits) < 5:
          c.date_a.day = join_digits(digits[:2])
          c.date_b.day = join_digits(digits[2:])
      elif len(digits) < 7:
          c.date_a.day = join_digits(digits[:2])
          c.date_b.month = join_digits(digits[2:4])
          c.date_b.day = join_digits(digits[5:])
      elif len(digits) < 11:
          c.date_a.day = join_digits(digits[:2])
          c.date_b.year = join_digits(digits[2:6])
          c.date_b.month = join_digits(digits[6:8])
          c.date_b.day = join_digits(digits[8:])
      tz = pytz.timezone("Asia/Seoul")
      vevent = cal.add('vevent')
      vevent.add('description').value = c.desc
      vevent.add('summary').value = c.desc
      vevent.add('dtstart').value = datetime(c.date_a.year, c.date_a.month, c.date_a.day, 0, 0, 0).astimezone(tz).date()
      vevent.add('dtend').value = datetime(c.date_b.year, c.date_b.month, c.date_b.day, 23, 59, 59).astimezone(tz).date()
      c.print()
  return cal


def main():
  cal = vobject.iCalendar()
  cal.add('prodid').value = AUTHOR
  url = "https://www.snu.ac.kr/academics/resources/calendar"
  txt = req.get(url).text # convert to url's html to string
  time.sleep(2) # todo: change to coroutine checking that task is done
  soup = bs(txt, "lxml") # generate BeautifulSoup class
  wrap = soup.select('div.work-wrap') # select calendar body
  thisyear = join_digits(extract_digits(soup.select_one('div.this-year').get_text()))
  # extract months and contents
  for x in wrap:
    cal = get_content(cal, x, get_date(x.select_one('span.month-text').get_text(), thisyear))

  if not os.path.exists(os.path.dirname(FILE_OUTPUT_PATH)):
      os.makedirs(os.path.dirname(FILE_OUTPUT_PATH))
  with open(FILE_OUTPUT_PATH, 'wb') as f:
    f.write(cal.serialize().encode('utf-8'))

if __name__ == "__main__":
  main()
