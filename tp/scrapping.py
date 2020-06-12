import urllib3
import pandas as pd
import re
from bs4 import BeautifulSoup


download = False

def clean_text(a_string):
  a_string = a_string.strip().replace('\t', '').replace('\n', '')
  all_text = re.search(r"^#([a-zA-Z0-9\-]*\s)(\((([^()]*|\([^()]*\))*)\))?(.+)\((.+)\)", a_string)
  dream_identification = all_text.group(1).strip()

  if all_text.group(3) is not None:
    dream_note = all_text.group(3)
  else:
    dream_note = None

  dream_description = all_text.group(5).strip()
  dream_words = int(re.search(r"\d+", all_text.group(6)).group())
  return [dream_identification, dream_note, dream_description, dream_words, True]


def get_dreams_from_web():
  url = 'http://www.dreambank.net/random_sample.cgi'

  http = urllib3.PoolManager()
  reponse = http.request('GET', url)
  main_table = BeautifulSoup(reponse.data, "html.parser")
  dream_series_options = main_table.find(
    "select", id = "select:series").find_all("option")

  df = pd.DataFrame()

  for a_serie in dream_series_options:
    print(f"Getting the dreams of: {a_serie.getText()}")
    reponse = http.request(
      'GET', url, 
      fields={'series': a_serie['value'], min: '1', 'max': '30000000', 'n': '1000000'})

    a_set_of_dreams = BeautifulSoup(reponse.data, 'html.parser').find_all('span')
    
    data = {'GroupDescription':[a_serie.getText()] * len(a_set_of_dreams),
      #'DreamNumber':[i+1 for i in range(len(a_set_of_dreams))],
      'CompleteDescription':[a_dream.getText() for a_dream in a_set_of_dreams]}
    df = pd.concat([df, pd.DataFrame(data)])
  
  df.to_csv("./data/dreams.csv", sep=";", index=False)


if __name__ == "__main__":
  if download:
    get_dreams_from_web()
    exit

  df = pd.read_csv('./data/dreams.csv', sep=';')
  summary = pd.read_csv('./data/dreamers_summary.csv', sep='|')

  print(df.shape)
  dreams_clean = []
  for dream_description in df['CompleteDescription']:
    try:
      dreams_clean.append(clean_text(dream_description))
    except:
      dreams_clean.append([None, None, dream_description, None, False])
    

  df_dreams_clean = pd.DataFrame(dreams_clean)
  df_dreams_clean.columns = ["code", "note", "description", "words", "parsed"]

  #df['group'] = df['GroupDescription'].apply(lambda x: re.sub(r'^(.+)(\s\[.+\])$', r'\1', x.strip()))
  group = []
  for row in df.itertuples():
    new_group = row.GroupDescription.strip().replace('  ', ' ')
    group.append(re.sub(r'^(.+)(\s\[.+\])$', r'\1', new_group))
  df['group'] = group

  df = pd.concat([df, df_dreams_clean], axis=1, sort=False)
  print(df.shape)

  total_words = []
  summary['id'] = list(range(1,len(summary)+1))
  df['group_id'] = -1

  for row in summary.itertuples():
    total_words.append(df.loc[df['group'] == row.group]['words'].sum())
    df.loc[df['group'] == row.group, 'group_id'] = row.id
  
  summary['total_words'] = total_words
  df.drop(['CompleteDescription', 'GroupDescription', 'group', 'parsed'], axis=1, inplace=True)

  df.to_csv("./data/dreams_clean.csv", sep=";", index=False)
  summary.to_csv("./data/dreamers_summary.csv", sep="|", index=False)
    